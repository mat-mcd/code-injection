import tkinter, os, threading, time, urllib.request, psutil, cpuinfo, shutil, subprocess, pythoncom, wmi
from tkinter import ttk
import customtkinter as ci
from app import settings
from app import data
from PIL import Image, ImageTk
from playsound import playsound
from datetime import date
from psutil._common import bytes2human
import tkfilebrowser as tkfilebrowser
from tkinter import messagebox
from app import logs
from pygame import mixer 

class backup(ci.CTkFrame):
    def __init__(self, master, window):
        self.window = window
        self.master = master
        self.user_data = data.UserData.get_instance()
        self.create_content()
        self.source_dir = False
        self.folder_save = False
        style = ttk.Style()
        style.theme_use("default")
        self.window.unbind('<Return>')
        self.window.bind('<Return>', self.threading) 
        self.is_running = False  

    def getFolderSize(self,folder):
        total_size = os.path.getsize(folder)
        for item in os.listdir(folder):
            itempath = os.path.join(folder, item)
            if os.path.isfile(itempath):
                total_size += os.path.getsize(itempath)
            elif os.path.isdir(itempath):
                total_size += self.getFolderSize(itempath)
        return total_size

    def human(self,size):
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

        return HUMANFMT % (size,  UNITS[-1])

    def select_folder_to_save(self):
        self.folder_save = tkfilebrowser.askopendirname(parent=self.frame, initialdir='/', title='Selecione o diretorio onde irá salvar o backup', okbuttontext='Confirmar', cancelbuttontext='Cancelar')       
        self.dir_save.delete(0, 'end')
        self.dir_save.insert(0, self.folder_save)

    def select_folders(self):
        self.source_dir = tkfilebrowser.askopendirnames(parent=self.frame, initialdir='/', title='Selecione o(s) diretorio(s) que deseja copiar', okbuttontext='Confirmar', cancelbuttontext='Cancelar')

        self.listbox.delete(0, 'end')
        for i in self.source_dir:
            self.listbox.insert(0, f"{i}\n")

    def threading(self, event=None):
        if self.is_running == True:
            pass
        else:
            self.is_running = True
            global t1
            t1=threading.Thread(target=self.copy_start)
            t1.start()
            self.progress.configure(text='')
            self.start.configure(state='disable')
            self.p = 0
            self.progress_bar_check()

    def progress_bar_check(self):
        if self.p != 99:
            if t1.is_alive():            
                self.p += 0.1
                self.progressbar.set(self.p)
                if self.p >= 1.0:
                    self.p = 0
                self.master.after(400, self.progress_bar_check)

    def copy_start(self):
        if not self.source_dir:
            messagebox.showinfo('Aviso do Sistema', 'Selecione as pastas que deseja fazer backup')
            self.start.configure(state='active')
        elif not self.folder_save:
            messagebox.showinfo('Aviso do Sistema', 'Selecione a pasta onde seja salvar o backup')
            self.start.configure(state='active')
        elif self.bk_nome.get() == "":
            messagebox.showinfo('Aviso do Sistema', 'Informe o nome da pasta do backup')
            self.start.configure(state='active')

        elif "\\" in self.bk_nome.get() or "/" in self.bk_nome.get():
            messagebox.showinfo('Aviso do Sistema', 'O nome da pasta do backup não deve conter barra(s)')
            self.start.configure(state='active')

        else:  
            pastas = ""
            today = date.today()

            for x in self.source_dir:
                pastas+=f'"{x}\\" '

            self.progress['text'] = "Copiando, aguarde..."        

            if settings.bits:
                fastcopy = 'fastcopy/64bits'
            else:
                fastcopy = 'fastcopy/32bits'

            to = f'{self.folder_save}/{self.bk_nome.get()} {today.strftime("%d-%m-%y")} {self.user_data.user_bk_name}/'    


            settings.terminal(f'{settings.folder_assets}/scripts/{fastcopy}/FastCopy.exe /cmd=force_copy /log /filelog /no_ui /balloon=FALSE /error_stop=FALSE /auto_close /force_close {pastas} /to="{to}"') 
            

            if self.debug.get() == 1:
                self.progress['text'] = "Coletando informações do computador, aguarde..."
                proxy = urllib.request.getproxies()
                total_memory = bytes2human(psutil.virtual_memory()[0])
                processor = cpuinfo.get_cpu_info()['brand_raw']
                pythoncom.CoInitialize()
                c = wmi.WMI()    
                systeminfo = c.Win32_ComputerSystem()[0]
                motherboard = str(systeminfo.Manufacturer+'  - '+systeminfo.Model).replace('  ', '')
                total, used, free = shutil.disk_usage("/")
                hdd_size = f'Total: {(total // (2**30))}GB | Usado: {(used // (2**30))}GB | Disponível: {(free // (2**30))}GB'
                

                domain = settings.terminal('Powershell.exe try{(Get-CimInstance Win32_ComputerSystem).Domain}Catch{(Get-WmiObject Win32_ComputerSystem).Domain}')
                         
                create_folder_new_name = to.replace('\\','/')
                create_folder_new_name = create_folder_new_name.replace('\\\\','/')
                try:
                    os.mkdir(f'{create_folder_new_name}[Logs]Backup/')  
                except:
                    pass

                from app import getprogramsinstalled
                with open(f"{to}[Logs]Backup/Programas.txt", "w") as file:
                    file.write(getprogramsinstalled.programs_installed_str)  

                subprocess.Popen(f'wmic process get description, processid > "{to}[Logs]Backup/Processos.txt"', shell=True, startupinfo=settings.startupinfo, creationflags=settings.disable_terminal)    
                subprocess.Popen(f'systeminfo > "{to}[Logs]Backup/Sistema.txt"', shell=True, startupinfo=settings.startupinfo, creationflags=settings.disable_terminal)    
                subprocess.Popen(f'ipconfig /all > "{to}[Logs]Backup/Rede.txt"', shell=True, startupinfo=settings.startupinfo, creationflags=settings.disable_terminal)    
                subprocess.Popen(f'wmic printer get Name, DriverName, Portname > "{to}[Logs]Backup/Impressoras.txt"', shell=True, startupinfo=settings.startupinfo, creationflags=settings.disable_terminal)    
  


                if os.path.isdir(f'C:\\Users\\{settings.pc_username}\\AppData\\Local\\Google\\Chrome\\User Data\\Default'):
                    try:
                        os.mkdir(f'{create_folder_new_name}[Logs]Backup/Google-Chorme-Backup')
                    except:
                        pass                     
                    gc_bookmarks = f'C:\\Users\\{settings.pc_username}\\AppData\\Local\\Google\\Chrome\\User Data\\Default\\Bookmarks'
                    gc_history = f'C:\\Users\\{settings.pc_username}\\AppData\\Local\\Google\\Chrome\\User Data\\Default\\History'
                    gc_links = f'C:\\Users\\{settings.pc_username}\\AppData\\Local\\Google\\Chrome\\User Data\\Default\\Visited Links'
                    settings.terminal(f'{settings.folder_assets}/scripts/{fastcopy}/FastCopy.exe /cmd=force_copy /log /filelog /no_ui /balloon=FALSE /error_stop=FALSE /auto_close /force_close "{gc_bookmarks}" "{gc_history}" "{gc_links}" /to="{to}[Logs]Backup/Google-Chorme-Backup"')    

                from app import getnetwork    
                txt = f'Informações do Sistema Operacional\nNome do Computador: {settings.pc_name}\nNome de Usuário: {settings.pc_username}\nGrupo de Trabalho/Domínio: {domain}\nRede:\n{getnetwork.networks}Proxy: {proxy}\nSistema: {settings.system} - {settings.version}\nData de Instalação do OS: {str(settings.os_date_install)}\nData do Backup: {settings.now.strftime("%d/%m/%Y %H:%M:%S")}\nUsuário que realizou o Backup:{str(self.user_data.user_name)}\n\nInformações do Computador\nMemória RAM: {total_memory}\nPlaca Mãe: {motherboard}\nProcessador: {processor}\nDisco[C:\\]: {hdd_size}\nSerial:{settings.serial_number()}\n\nPara informações mais detalhadas visualize os outros arquivos gerados nesta mesma pasta\n{settings.app_name} v{settings.app_version}'     

                save_txt = open(f'{to}[Logs]Backup/Code-Injection.txt', "w")
                save_txt.write(txt)
                save_txt.close()

    
            try:
                mixer.init()
                self.driver_found = True
            except Exception as e:
                self.driver_found = False

            if self.driver_found:
                mixer.Channel(0).play(mixer.Sound(settings.folder_assets+"/audio/alerta.mp3"))
                time.sleep(1)
                mixer.Channel(0).play(mixer.Sound(settings.folder_assets+"/audio/backup.mp3"))

            x = to.replace("\\", "/")
            total_copy = str(self.human(self.getFolderSize(x)))
            if settings.dev_mode == False:    
                logs.add.insert_log(self, f"Fez Backup - PC: {settings.pc_name} | USUÁRIO: {settings.pc_username} | {total_copy}")
            

            self.p = 99
            self.progress.configure(text="Backup finalizado")
            self.start.configure(state='active')    
            self.is_running = False
            self.progressbar.set(1)

            if self.debug.get() == 0:
                messagebox.showinfo('Aviso do Sistema',f'Backup Finalizado!\nTotal copiado: {str(self.human(self.getFolderSize(x)))}')
            else:
                messagebox.showinfo('Aviso do Sistema',f'Backup Finalizado!\n\nTotal copiado: {str(self.human(self.getFolderSize(x)))}\n\nFoi criado a pasta "[Logs]Backup" em \n{x}\ndentro você encontrará todas as informações coletadas')     
            subprocess.Popen(f'explorer /select, "{x}"', shell=True, startupinfo=settings.startupinfo, creationflags=settings.disable_terminal)    
  
    


    def create_content(self):
        self.frame = ci.CTkFrame(self.master, width=800, height=600)
        self.frame.pack(pady=25, fill='both')
        self.page = ci.CTkLabel(self.frame, text="BACKUP", text_font=("Roboto Medium", 20))
        self.page.place(relx=0.41, rely=0.01)

        self.select1 = ci.CTkButton(self.frame, text='Fonte', text_font=(settings.code_injection['style']['font'], -13), command=self.select_folders)
        self.select1.place(rely=0.14, relx=0.06)

        if settings.code_injection['style']['theme'] == 'light':
            color = 'gray30'
        else:
            color = 'gray75'
            
        self.listbox = tkinter.Listbox(self.frame, bg=settings.font_color, selectbackground=settings.bg_color, fg=color, height=6, width=55, font=(settings.code_injection['style']['font'], 11), bd=0, highlightbackground=settings.bg_color, highlightthickness=3)
        self.listbox.place(rely=0.135, relx=0.28)

        self.select2 = ci.CTkButton(self.frame, text='Destino', text_font=(settings.code_injection['style']['font'], -13), command=self.select_folder_to_save)
        self.select2.place(rely=0.435, relx=0.06)


        self.dir_save = ci.CTkEntry(master=self.frame, corner_radius=3, width=445, height=37)
        self.dir_save.place(rely=0.43, relx=0.28)

        self.bk_nome_b = ci.CTkButton(self.frame, text='Nome', text_font=(settings.code_injection['style']['font'], -13))
        self.bk_nome_b.place(rely=0.55, relx=0.06)

        self.bk_nome = ci.CTkEntry(master=self.frame, placeholder_text="Exemplo: Backup Mateus", corner_radius=3, width=445, height=37)
        self.bk_nome.place(rely=0.55, relx=0.28)

        self.debug = ci.CTkCheckBox(master=self.frame, text=' Salvar informações do computador',  text_font=("Roboto Medium", -17))
        self.debug.place(rely=0.67, relx=0.28)
        self.debug.select()

        ci.CTkLabel(self.frame, text="Informações do Sistema Operacional, Informações de Hardware", text_font=(settings.code_injection['style']['font'], 10)).place(rely=0.71, relx=0.32)
        ci.CTkLabel(self.frame, text="Programas e Impressoras instalados, processos e outros", text_font=(settings.code_injection['style']['font'], 10)).place(rely=0.75, relx=0.32)


        self.progress = ci.CTkLabel(self.frame, text='', text_font=(settings.code_injection['style']['font'], 12))
        self.progress.place(rely=0.87, relx=0.06)   


        self.progressbar = ci.CTkProgressBar(master=self.frame, width=510, height=14)
        self.progressbar.place(rely=0.93, relx=0.06)
        self.progressbar.set(0)


        start_img = ImageTk.PhotoImage(Image.open(settings.folder_assets+f"/img/icons/{settings.icon_start}"))
        self.start = ci.CTkButton(master=self.frame, image=start_img, text='', hover_color=None, fg_color=("#DEDEDE", "#2E2E2E"), command=self.threading)
        self.start.place(relx=0.80, rely=0.90)

