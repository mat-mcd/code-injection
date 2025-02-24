import customtkinter as ci
import threading, wget, socket, requests, os, sys, ctypes, configparser
from zipfile import ZipFile
from tkinter import ttk, messagebox
from PIL import Image, ImageTk

try:
    import pyi_splash
    pyi_splash.update_text('Carregando...')
    pyi_splash.close()
except:
    pass

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

if not is_admin():
    messagebox.showerror('Aviso do Sistema', 'O atualizador não foi iniciado com permissões de administrador')
    sys.exit()

if len(sys.argv) == 1:
    messagebox.showerror('Aviso do Sistema', 'Oops, ocorreu um erro\n\nAcesso direto não é permitido.')
    sys.exit()

code_injection = configparser.ConfigParser()
code_injection.read(sys.argv[1]+'/configs/code-injection.ini')

def edit_ini(file_path, section, key, value):
    config = configparser.ConfigParser()
    config.read(file_path)
    config.set(section,key,value)                         
    cfgfile = open(file_path,'w')
    config.write(cfgfile, space_around_delimiters=False) 
    cfgfile.close()


def check_network():
    try:
        sock = socket.create_connection(("www.google.com", 80))
        if sock is not None:
            sock.close
        return True
    except OSError:
        pass
    return False

def bar_progress(current, total, width=80):
  size_total = total
  size_download = current
  perc =  int((current / total * 100))
  pb1['value'] = perc
  root_update.title(f"Atualizando {perc}%  - Code Injection")
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
            r = requests.post(code_injection['update']['url_check_update'])
            result = r.json()
            new_version = result['version']

            if code_injection['app']['version'] < new_version:
                
                if os.path.exists(result['download']):
                    os.remove(result['download'])
                os.system('taskkill /f /im '+code_injection['update']['exe_file']+'')
                d = wget.download(code_injection['update']['url_download_updates']+'/'+result['download'], bar=bar_progress)
                file = ZipFile(result['download'])
                file.extractall()
                file.close()
                os.remove(result['download'])


                mts = os.listdir(".")
                for item in mts:
                    if item.endswith(".tmp"):
                        os.remove(os.path.join("", item))
                edit_ini(sys.argv[1]+'/configs/code-injection.ini', 'app', 'version', str(new_version))
                edit_ini(sys.argv[1]+'/configs/code-injection.ini', 'app', 'hide_changelog', 'false')
                info_label.configure(text_color="#0E9670")
                info_label["text"] = f"Nova Versão Instalada: v{str(new_version)}"
            else:
                info_label["text"] = f"Você já possui a última versão (v{str(new_version)})"
                pb1['value'] = 100

        except Exception as e:
            messagebox.showinfo("Aviso do Sistema", 'Oops, ocorreu um erro\n\n'+str(e))
    else:
        info_label.configure(text_color= "#f91111")
        info_label['text'] = 'Sem conexão com a internet'


def schedule_check(t):
    root_update.after(1000, check_if_done, t)


def check_if_done(t):
    schedule_check(t)


ci.set_appearance_mode(code_injection['style']['theme'].capitalize())  
ci.set_default_color_theme(code_injection['style']['color'])
root_update = ci.CTk()
root_update.geometry("350x250")
root_update.title("Atualização - Code Injection")
root_update.iconbitmap(sys.argv[1]+'/img/code-injection.ico')
root_update.resizable(0,0)


if code_injection['style']['theme'] == 'dark':
    logo_file = sys.argv[1]+"/img/code-injection[dark].png"
else:
    logo_file = sys.argv[1]+"/img/code-injection[light].png"


image = Image.open(logo_file)
logo = ImageTk.PhotoImage(image)
label1 = ci.CTkLabel(root_update,image=logo, text='')

label1.image = logo
label1.place(x=45, y=20)

info_label = ci.CTkLabel(root_update,text="Verificando se há uma nova versão...", text_font=(code_injection['style']['font'], 11), background='#ffffff')
info_label.place(x=25, y=160)

pb1 = ttk.Progressbar(root_update,length=300, mode='determinate')
pb1.place(x=25, y=190)


t = threading.Thread(target=download_file_worker)
t.start()
schedule_check(t)
root_update.mainloop()
