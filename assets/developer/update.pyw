import threading, wget, socket, requests, json, os, pyglet, sys
from tkinter import *
from tkinter import ttk
from zipfile import ZipFile
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
from tkinter.messagebox import askyesno

if len(sys.argv) == 1:
    import pymsgbox 
    pymsgbox.alert('Acesso direto não permitido\nDefina o local da pasta raiz via argumentos', 'Aviso do Sistema')
    sys.exit()

json_open = open(sys.argv[1]+'json/settings.json')
json = json.loads(json_open.read())

def check_network():
    try:
        sock = socket.create_connection(("www.google.com", 80))
        if sock is not None:
            sock.close
        return True
    except OSError:
        pass
    return False

def replace_line(file_name, line_num, text):
    lines = open(file_name, 'r').readlines()
    lines[line_num] = text
    out = open(file_name, 'w')
    out.writelines(lines)
    out.close()

def bar_progress(current, total, width=80):
  size_total = total
  size_download = current
  perc =  int((current / total * 100))
  pb1['value'] = perc
  root.title(f"Atualizando {perc}%  - Code Injection")
  info_label["text"] = f'Baixando {human(size_download)} de {human(size_total)}'

def human(size):
    B = "B"
    KB = "KB" 
    MB = "MB"
    GB = "GB"
    TB = "TB"
    UNITS = [B, KB, MB, GB, TB]
    HUMANFMT = "%f %s"
    HUMANRADIX = 1024.

    for u in UNITS[:-1]:
        if size < HUMANRADIX : return HUMANFMT % (size, u)
        size /= HUMANRADIX

    return int(HUMANFMT) % (size, UNITS[-1])


def download_file_worker():
    if check_network():
        try:
            r = requests.post(json['url_check_update'])
            result = r.json()
            new_version = result['version']

            if json['app_version'] < new_version:
                
                if os.path.exists(result['download']):
                    os.remove(result['download'])
                os.system('taskkill /f /im '+json['exe_file']+'')
                d = wget.download(json['url_download_updates']+'/'+result['download'], bar=bar_progress)
                file = ZipFile(result['download'])
                file.extractall()
                file.close()
                os.remove(result['download'])


                mts = os.listdir(".")
                for item in mts:
                    if item.endswith(".tmp"):
                        os.remove(os.path.join("", item))
                replace_line(sys.argv[1]+'json/settings.json', 7, f'"app_version":"{str(new_version)}",\n')
                replace_line(sys.argv[1]+'json/settings.json', 8, f'"show_terms":"true",\n')
                info_label.config(fg= "green")
                info_label["text"] = f"Nova Versão Instalada: v{str(new_version)}"
                messagebox.showinfo("Atualização concluída", 'Sistema atualizado com sucesso!') 
            else:
                info_label["text"] = f"Você já possui a última versão (v{str(new_version)})"
                pb1['value'] = 100

        except Exception as e:
            messagebox.showinfo("Aviso do Sistema", 'Ocorreu um erro\n\n'+str(e))
    else:
        info_label.config(fg= "red")
        info_label['text'] = 'Sem conexão com a internet'
        


def schedule_check(t):
    root.after(1000, check_if_done, t)


def check_if_done(t):
    schedule_check(t)


root = Tk()
root.geometry('350x250')
root.configure(background='#ffffff')
root.iconbitmap(sys.argv[1]+'images/icon.ico')
root.resizable(0,0)
root.title("Central de Atualização - Code Injection")
pyglet.font.add_file(sys.argv[1]+'scripts/code-injection.ttf')

image1 = Image.open(sys.argv[1]+'images/logo.png')
test = ImageTk.PhotoImage(image1)

label1 = Label(image=test,background='#ffffff')
label1.image = test
label1.place(x=25, y=5)


info_label = Label(text="Verificando se há uma nova versão...", font=('Segoe UI Variable Static Text', 11), background='#ffffff')
info_label.place(x=25, y=160)


pb1 = ttk.Progressbar(length=300, mode='determinate')
pb1.place(x=25, y=190)

t = threading.Thread(target=download_file_worker)
t.start()
schedule_check(t)
root.mainloop()