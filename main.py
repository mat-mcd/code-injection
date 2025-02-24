import soundcard as sc
import customtkinter as ci
import multiprocess, pyglet, os, datetime, shutil, threading, random, ctypes, sys, hashlib, cryptocode, requests
from PIL import Image, ImageTk
from app import settings
from app import data
from tkinter import filedialog, messagebox
from tkinter.ttk import * 


if settings.code_injection['playlist']['background_music'] == 'true':
    from pygame import mixer
    from pygame import USEREVENT
    from pygame import event
    from pygame import display

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

if not is_admin():
    messagebox.showinfo("Aviso do Sistema", "O programa não foi iniciado com permissões de administrador\nAlgumas funções pode não funcionar corretamente")

def reset_license():
    try:
        if settings.check_network():
            check_settings = settings.c.execute("SELECT * FROM settings")
            row = check_settings.fetchall()
            serial_decrypt = cryptocode.decrypt(row[0][0], settings.secret_key)
            user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36"
            headers = {
                "User-Agent": user_agent
            }
            requests.get(settings.url_check_license+f'get-device.php?serial={serial_decrypt}&device_id=0&device_name=0', headers=headers)
            data = [0,0,0]
            settings.c.execute("UPDATE settings set serial_license=?, device_id=?, device_name=?", data)
            settings.db.commit()
            print("license reset")
        else:
            print("you need to be connected to the internet to reset the license")
    except Exception as e:
        print(f'fail reset license\n\n{e}')

def reset_users():
    new_password = hashlib.md5(settings.prefix_password+'12345'.encode('utf8')).hexdigest() 
    settings.c.execute("UPDATE users set password=?", [new_password])
    settings.db.commit()
    print("users reset") 

def reset_logs():
    settings.c.execute("DELETE FROM logs")
    settings.db.commit()
    print("deleted logs")

def reset_ini():
    try:
        user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36"
        headers = {
            "User-Agent": user_agent
        }
        response = requests.get(settings.url_check_license+f'code-injection.ini', headers=headers) 
        arq = open(settings.folder_assets+'/configs/code-injection.ini', 'w')
        arq.write(str(response.text))
        arq.close()
        print('ini file reseted')
    except Exception as e:
        print(f'fail reset ini file\n\n{e}')

if len(sys.argv) > 1:
    if sys.argv[1] == "reset-license":
        reset_license()

    elif sys.argv[1] == "reset-users":
        reset_users()

    elif sys.argv[1] == "reset-logs":
        reset_logs() 

    elif sys.argv[1] == "reset-ini":
        reset_ini()

    elif sys.argv[1] == "reset-all":
        reset_license()
        reset_users()
        reset_logs()
        reset_ini()
    else:
        pass
        
try:
    import pyi_splash
    pyi_splash.update_text('Carregando...')
    pyi_splash.close()
except:
    pass
    
ci.set_appearance_mode(settings.code_injection['style']['theme'].capitalize())  
ci.set_default_color_theme(settings.code_injection['style']['color']) 

class App(ci.CTk):
    def __init__(self):
        super().__init__()
        pyglet.font.add_file(settings.folder_assets+'/scripts/segoe.ttf')
        self.init = True
        self.logged = False
        self.focus_force()

        if self.logged == False:
            if settings.code_injection['app']['hide_changelog'] == 'true':
                self.login()
            else:
                self.changelog()
        else:
            self.create_base()  

            if settings.code_injection['playlist']['background_music'] == "true" and settings.code_injection['playlist']['startup_music'] == 'pause':
                self.play.configure(image=self.play_img)
                self.is_paused = 1
                self.__pause_unpause_music()

    if settings.code_injection['playlist']['background_music'] == 'true':
        def __check_end(self):
            for e in event.get():
                if e.type == USEREVENT:
                    self.__next_music()

            self.after(100, self.__check_end)

        def __volume(self, value):
            mixer.music.set_volume(self.volume.get())
            settings.edit_ini('playlist', 'volume', str(self.volume.get()))


        def __get_music(self):
            self.music_files = os.listdir(settings.folder_assets+'/audio/playlist')

        def __play_music(self, music):
            try:
                display.init()
                mixer.music.set_volume(float(settings.code_injection['playlist']['volume']))            
                mixer.music.load(settings.folder_assets+'/audio/playlist/'+music)
                mixer.music.fadeout(5)
                
                if self.is_paused == 1:
                    mixer.music.play()
                    mixer.music.pause()
                else:
                    mixer.music.play()
                    self.is_paused = 0
                mixer.music.set_endevent(USEREVENT)

            except Exception as e:
                settings.notification(f'Ocorreu um erro ao reproduzir sua playlist\n\n{e}', 15)

        def __start_music(self):
            random_music = random.choice(self.music_files)
            self.__play_music(random_music)
            self.atual_music = self.music_files.index(random_music)

        def __pause_unpause_music(self):
            if self.is_paused == 0:
                mixer.music.pause()
                self.play.configure(image=self.play_img)
                self.is_paused = 1
            else:
                mixer.music.unpause()
                self.play.configure(image=self.pause_img)
                self.is_paused = 0
            
        def __next_music(self):
            self.atual_music += 1
            if self.atual_music >= self.musics_num:
                self.__play_music(self.music_files[0])
                self.atual_music = 0
            else:
                self.__play_music(self.music_files[self.atual_music])

        def __back_music(self):
            if self.atual_music == 0:
                self.atual_music = len(self.music_files) - 1
                self.__play_music(self.music_files[self.atual_music])
            else:
                self.atual_music -= 1
                self.__play_music(self.music_files[self.atual_music])


    def confirm(self):
        from tkinter.messagebox import askyesno
        answer = askyesno(title='Aviso do Sistema',
                        message='Tem certeza de que deseja sair?')
        if answer:
            self.on_closing()

    def update_photo(self):
        self.user_data = data.UserData.get_instance()
        self.file = filedialog.askopenfilename(title='Selecione a nova imagem para o seu perfil',filetypes=[('', '*jpg *png *jpeg')])
        if self.file:                       
            img_=Image.open(self.file)
            image2=img_.resize((110,110),Image.ANTIALIAS)
            img_code=ImageTk.PhotoImage(image2)
            self.avatar.configure(image=img_code)
            self.avatar.image = img_code
            filename = self.file
            avatar = datetime.datetime.now()
            avatar = self.user_data.user_user+'_'+avatar.strftime("%f")+'.png'            
            shutil.copy(filename, f'{settings.folder_assets}/img/avatar/{avatar}')

            sqliteConnection = settings.db
            cursor = settings.c
            sqlite_insert_query = """UPDATE users SET
                          avatar='{}' WHERE username='{}'
                          """.format(avatar, self.user_data.user_user)

            cursor.execute(sqlite_insert_query)
            sqliteConnection.commit()
            self.user_data.set_avatar(str(avatar))

            messagebox.showinfo('Aviso do Sistema', 'Sua foto de perfil foi atualizada')  

    def create_base(self):
        self.focus_force()
        if settings.code_injection['playlist']['background_music'] == 'true':
            try:
                mixer.init()
                self.driver_found = True
            except Exception as e:
                settings.notification(f'Playlist - nenhuma saída de audio encontrada\n{e}', 15)
                self.driver_found = False

            if self.driver_found:    
                self.atual_music = 0
                self.is_paused = 0
                self.__get_music()
                self.__start_music()
                self.__check_end()
                self.musics_num = len(self.music_files)
        self.user_data = data.UserData.get_instance()
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.grid_columnconfigure(1, weight=100)
        self.rowconfigure(0, weight=100)
        self.geometry('950x660+10+10')
        self.resizable(0,0)
        self.iconbitmap(settings.folder_assets+"/img/code-injection.ico")
        self.frame_left = ci.CTkFrame(master=self,width=100,corner_radius=0)
        self.frame_left.grid(row=0, column=0, sticky="nswe")

        self.frame_left.grid_rowconfigure(2, minsize=0) 
        self.frame_left.grid_rowconfigure(12, weight=1) 

        if os.path.isfile(settings.folder_assets+'/img/avatar/'+self.user_data.user_avatar):
            image = Image.open(settings.folder_assets+'/img/avatar/'+self.user_data.user_avatar)
            image=image.resize((110,110),Image.ANTIALIAS)
        else:
            image = Image.open(settings.folder_assets+"/img/avatar/avatar.png")
            image=image.resize((110,110),Image.ANTIALIAS)

        self.bg_image = ImageTk.PhotoImage(image)

        self.label = ci.CTkFrame(master=self.frame_left, height=1)
        self.label.grid(row=0, column=0, pady=10)

        if settings.code_injection['playlist']['background_music'] == 'true':
            settings_img = ImageTk.PhotoImage(file=settings.folder_assets+"/img/icons/settings.png")
            self.settings_btn = ci.CTkButton(self.frame_left, image=settings_img, width=35, text='', hover_color=None, fg_color=("#DEDEDE", "#2E2E2E"), command=self.config)
            self.settings_btn.image = settings_img
            self.settings_btn.place(relx=0.82, rely=0.008)


        self.avatar = ci.CTkButton(master=self.frame_left, image=self.bg_image, text="", fg_color=("gray70", "gray25"), hover_color="gray35", command=self.update_photo)
        self.avatar.grid(row=1, column=0)

        self.frame = ci.CTkFrame(master=self.frame_left, corner_radius=0)
        self.frame.grid(row=2, column=0, pady=10)


        self.name = ci.CTkLabel(master=self.frame, text=self.user_data.user_name, text_font=("Roboto Medium", -21))
        self.name.pack()

        self.name = ci.CTkLabel(master=self.frame, text=self.user_data.user_role, text_font=("Roboto Medium", -14))
        self.name.pack()

        self.frame_left.grid_rowconfigure(2, minsize=0) #bottom

        self.btn_sysinfo = ci.CTkButton(master=self.frame_left, width=180, text="SysInfo", fg_color=("gray75", "gray30"), text_font=(settings.code_injection['style']['font'], -15), command=self.sysinfo)
        self.btn_sysinfo.grid(row=4, column=0, pady=6, padx=20)

        self.btn_install = ci.CTkButton(master=self.frame_left, width=180,text="Instalar Aplicativos", fg_color=("gray75", "gray30"), text_font=(settings.code_injection['style']['font'], -15), command=self.install_apps)
        self.btn_install.grid(row=5, column=0, pady=6, padx=20)

        self.btn_function = ci.CTkButton(master=self.frame_left, width=180, text="Funções",fg_color=("gray75", "gray30"), text_font=(settings.code_injection['style']['font'], -15), command=self.function)
        self.btn_function.grid(row=6, column=0, pady=6, padx=20)

        self.btn_tools = ci.CTkButton(master=self.frame_left, width=180, text="Ferramentas",fg_color=("gray75", "gray30"), text_font=(settings.code_injection['style']['font'], -15), command=self.tools)
        self.btn_tools.grid(row=7, column=0, pady=6, padx=20)

        self.btn_backup = ci.CTkButton(master=self.frame_left, width=180, text="Backup",fg_color=("gray75", "gray30"), text_font=(settings.code_injection['style']['font'], -15), command=self.backup)
        self.btn_backup.grid(row=8, column=0, pady=6, padx=20)

        self.btn_myaccount = ci.CTkButton(master=self.frame_left, width=180, text="Minha conta",fg_color=("gray75", "gray30"), text_font=(settings.code_injection['style']['font'], -15), command=self.myaccount)
        self.btn_myaccount.grid(row=9, column=0, pady=6, padx=20)

        self.btn_logs = ci.CTkButton(master=self.frame_left, width=180, text="Logs",fg_color=("gray75", "gray30"), text_font=(settings.code_injection['style']['font'], -15), command=self.logs)
        self.btn_logs.grid(row=10, column=0, pady=6, padx=20)

        self.btn_logout = ci.CTkButton(master=self.frame_left, width=180, text="Sair",fg_color=("gray75", "gray30"), text_font=(settings.code_injection['style']['font'], -15) ,command=self.confirm)
        self.btn_logout.grid(row=11, column=0, pady=6, padx=20)

        self.frame = ci.CTkFrame(master=self.frame_left, corner_radius=0)
        self.frame.grid(row=12, column=0)

        self.error = ci.CTkLabel(master=self.frame, text='', text_font=(settings.code_injection['style']['font'], -12))
        self.error2 = ci.CTkLabel(master=self.frame, text='', text_font=(settings.code_injection['style']['font'], -11))

        if settings.code_injection['playlist']['background_music'] == 'true' and self.driver_found == False:
            self.error.place(relx=0.01, rely=0.1)
            self.error2.place(relx=0, rely=0.28)
            self.error.configure(text='O player não foi iniciado', text_color='#f91111')
            self.error2.configure(text='Nenhuma saída de som encontrada', text_color='#f91111')
        else:
            if settings.code_injection['style']['color'] == 'blue' or settings.code_injection['style']['color'] == 'dark-blue':
                set_color = 1
                set_bg = '#21A5E6'
            else:
                set_color = 2
                set_bg = '#37B59C'

            if settings.code_injection['playlist']['background_music'] == 'true':
                play = Image.open(settings.folder_assets+f'/img/icons/play[{set_color}].png')
                play = play.resize((25,25),Image.ANTIALIAS)
                self.play_img = ImageTk.PhotoImage(play)

                pause = Image.open(settings.folder_assets+f'/img/icons/pause[{set_color}].png')
                pause = pause.resize((25,25),Image.ANTIALIAS)
                self.pause_img = ImageTk.PhotoImage(pause)

                self.play = ci.CTkButton(master=self.frame, image=self.pause_img, text="", fg_color=("#DEDEDE", "#2E2E2E"), hover_color=None, command=self.__pause_unpause_music)
                self.play.place(relx=0.16, rely=0.1)

                if settings.code_injection['playlist']['startup_music'] == "pause":
                    self.play.configure(image=self.play_img)
                    self.__pause_unpause_music()
                    
                image = Image.open(settings.folder_assets+f'/img/icons/back[{set_color}].png')
                image=image.resize((35,35),Image.ANTIALIAS)
                self.image = ImageTk.PhotoImage(image)
                self.back = ci.CTkButton(master=self.frame, image=self.image, text="", width=20, fg_color=("#DEDEDE", "#2E2E2E"), hover_color=None, command=self.__back_music)
                self.back.place(relx=0.215, rely=0.07)

                image = Image.open(settings.folder_assets+f'/img/icons/next[{set_color}].png')
                image=image.resize((35,35),Image.ANTIALIAS)
                self.image = ImageTk.PhotoImage(image)
                self.next = ci.CTkButton(master=self.frame, image=self.image, text="", width=20, fg_color=("#DEDEDE", "#2E2E2E"), hover_color=None, command=self.__next_music)
                self.next.place(relx=0.587, rely=0.07)

                self.volume = ci.CTkSlider(self.frame, to=1, from_=0, progress_color=set_bg, button_color=set_bg, number_of_steps=100, width=120, command=self.__volume)
                self.volume.place(relx=0.195, rely=0.43)
                self.volume.set(float(settings.code_injection['playlist']['volume']))

        if settings.code_injection['playlist']['background_music'] == 'false':
            settings_img = ImageTk.PhotoImage(file=settings.folder_assets+"/img/icons/settings.png")
            self.settings_btn = ci.CTkButton(self.frame, image=settings_img, width=35, text='', hover_color=None, fg_color=("#DEDEDE", "#2E2E2E"), command=self.config)
            self.settings_btn.image = settings_img
            self.settings_btn.pack()
            self.version = ci.CTkLabel(master=self.frame,text=f"{settings.app_name} v{settings.app_version}",  text_font=(settings.code_injection['style']['font'], -13))
            self.version.pack()

        else:    
            self.version = ci.CTkLabel(master=self.frame,text=f"{settings.app_name} v{settings.app_version}",  text_font=(settings.code_injection['style']['font'], -13))
            self.version.place(relx=0.19, rely=0.65)

        self.frame_right = ci.CTkFrame(master=self)
        self.frame_right.grid(row=0, column=1, sticky="nswe", padx=20, pady=20)
        self.loading = ci.CTkLabel(self.frame_right, text='Carregando...')
        self.loading.pack()

        if settings.dev_mode:
            self.config()
        else:
            self.sysinfo()

    def clear_frame(self):
        if not self.init:
            try:
                self.frame_right.destroy()
            except:
                pass
            self.btn_sysinfo.configure(fg_color=("gray75", "gray30"))
            self.btn_install.configure(fg_color=("gray75", "gray30"))
            self.btn_backup.configure(fg_color=("gray75", "gray30"))
            self.btn_function.configure(fg_color=("gray75", "gray30"))
            self.btn_logs.configure(fg_color=("gray75", "gray30"))
            self.btn_myaccount.configure(fg_color=("gray75", "gray30"))
            self.btn_tools.configure(fg_color=("gray75", "gray30"))
            
            self.frame_right = ci.CTkFrame(master=self)
            self.frame_right.grid(row=0, column=1, sticky="nswe", padx=20, pady=20)
            self.loading = ci.CTkLabel(self.frame_right, text='Carregando...', text_font=(settings.code_injection['style']['font'], -22))
            self.loading.pack(pady=40)    
            self.init = True     

    def login(self):
        from app.pages.login import login
        login(self)

    def changelog(self):
        from app.pages.changelog import changelog
        changelog(self)

    def sysinfo(self):
        from app.pages.sysinfo import SysInfo
        self.clear_frame()
        self.title(f'SysInfo - {settings.app_name} v{settings.app_version}')        
        SysInfo(master = self.frame_right)
        self.btn_sysinfo.configure(fg_color=settings.hover_color)
        self.init = False
        self.loading.pack_forget()

    def install_apps(self):
        self.clear_frame()
        from app.pages.installapps import InstallApps
        self.clear_frame()
        self.title(f'Instalar Aplicativos - {settings.app_name} v{settings.app_version}')
        InstallApps(master = self.frame_right, window = self)
        self.btn_install.configure(fg_color=settings.hover_color)
        self.init = False
        self.loading.pack_forget()

    def function(self):
        from app.pages.function import function
        self.clear_frame()
        self.title(f'Funções - {settings.app_name} v{settings.app_version}')
        function(master = self.frame_right, window = self)
        self.btn_function.configure(fg_color=settings.hover_color)
        self.init = False
        self.loading.pack_forget()

    def backup(self):
        from app.pages.backup import backup
        self.clear_frame()
        self.title(f'Backup - {settings.app_name} v{settings.app_version}')        
        backup(master = self.frame_right, window = self)
        self.btn_backup.configure(fg_color=settings.hover_color)
        self.init = False
        self.loading.pack_forget()

    def myaccount(self):
        from app.pages.myaccount import myaccount
        self.clear_frame()
        self.title(f'Minha conta - {settings.app_name} v{settings.app_version}')        
        myaccount(master = self.frame_right)
        self.btn_myaccount.configure(fg_color=settings.hover_color)
        self.init = False
        self.loading.pack_forget()

    def tools(self):
        from app.pages.tools import tools
        self.clear_frame()
        self.title(f'Ferramentas - {settings.app_name} v{settings.app_version}')        
        tools(master = self.frame_right)
        self.btn_tools.configure(fg_color=settings.hover_color)
        self.init = False
        self.loading.pack_forget()

    def config(self):
        from app.pages.config import config
        self.clear_frame()
        self.title(f'Configurações - {settings.app_name} v{settings.app_version}')        
        config(master = self.frame_right)
        self.init = False
        self.loading.pack_forget()

    def logs(self):
        from app.pages.logs import logs
        self.clear_frame()
        self.title(f'Logs - {settings.app_name} v{settings.app_version}')        
        logs(master = self.frame_right)
        self.btn_logs.configure(fg_color=settings.hover_color)
        self.init = False
        self.loading.pack_forget()

    def on_closing(self, event=0):
        from sys import exit
        if settings.dev_mode == False:
            try:
                from app import logs
                logs.add.insert_log(self, "Fez Logout")
            except:
                pass
        try:
            self.destroy()
            self.quit()            
            exit()
        except:
            exit()


if __name__ == "__main__":
    multiprocess.freeze_support()
    app = App()
    app.mainloop()


'''
Install - Python310
Install - https://visualstudio.microsoft.com/pt-br/visual-cpp-build-tools/
pip install -r requirements.txt
debug = pyflakes main.py

pegar imports
pipreqs --encoding=utf8 codeinjection/

%userprofile%/AppData/Roaming/Python/Python310/site-packages/customtkinter/assets/themes
    "frame_low": ["#DEDEDE", "#2E2E2E"],
    "frame_high": ["#DEDEDE", "#2E2E2E"],

%userprofile%/AppData/Local/Programs/Python/Python310/Lib/site-packages/customtkinter/__init__.py
add > warnings.filterwarnings("ignore")

%userprofile%/AppData/Local/Programs/Python/Python310/Lib/site-packages/customtkinter
%userprofile%/AppData/Roaming/Python/Python310/site-packages/customtkinter
customtkinter/

%userprofile%/AppData/Local/Programs/Python/Python310/Lib/site-packages/tkfilebrowser/images
%userprofile%/AppData/Roaming/Python/Python310/site-packages/tkfilebrowser/images
tkfilebrowser
ou
tkfilebrowser/images
'''
