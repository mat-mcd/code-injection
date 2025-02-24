import tkinter, threading, os, datetime, sys, subprocess, shutil
import customtkinter as ci
from tkinter import ttk, filedialog, messagebox
from app import settings
from app import data
from app import logs
from mutagen.mp3 import MP3
from tkinter.messagebox import askyesno

class config(ci.CTkFrame):
    def __init__(self, master):
        self.master = master
        self.user_data = data.UserData.get_instance()
        style = ttk.Style()
        style.theme_use("clam")
        self.create_content()

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    def onFrameConfigure(self,canvas):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def restore_apps(self):
        if self.restore_apps.get() == 1:
            settings.edit_ini('app', 'restore_point_apps', 'true')
        else:
            settings.edit_ini('app', 'restore_point_apps', 'false')

    def restore_function(self):
        if self.restore_function.get() == 1:
            settings.edit_ini('app', 'restore_point_func', 'true')
        else:
            settings.edit_ini('app', 'restore_point_func', 'false')

    def background_music(self):
        if self.playlist.get() == 1:
            settings.edit_ini('playlist', 'background_music', 'true')
        else:
            settings.edit_ini('playlist', 'background_music', 'false')

    def play_pause(self):
        if self.play_pause.get() == 1:
            settings.edit_ini('playlist', 'startup_music', 'pause')
        else:
            settings.edit_ini('playlist', 'startup_music', 'play')


    def delet_music(self):
        answer = askyesno(title='Aviso do Sistema', message=f'Realmente deseja deletar as musicas selecionadas ?')
        if answer:
            for i in range(len(self.selected)):
                if self.selected[i].get() == 1:
                    os.remove(settings.folder_assets+"/audio/playlist/"+self.music_files[i])
            self.music_frame.destroy()
            self.music_frame = ci.CTkFrame(self.playlist_musics_frame, fg_color=("gray75", "gray30"))
            self.music_frame.pack()
            self.load_music_frame_musics()
        else:
            pass

    def add_music(self):
        folder = f'{os.path.abspath(os.getcwd())}\\{settings.folder_assets}\\audio\\playlist\\'
        folder = folder.replace('\\', '/')
        messagebox.showinfo('Aviso do Sistema', f'Dica:\nPara adicionar novas música rapidamente basta copiar suas músicas favoritas em formato .mp3 para a pasta\n{folder}\n\n')
        self.file = filedialog.askopenfilename(title='Adicionar nova música',filetypes=[('Somente arquivos:', '*mp3')])
        if self.file:
            music = os.path.basename(self.file).replace(' ', '-')    
            shutil.copy(self.file, f'{settings.folder_assets}/audio/playlist/{music}')

            messagebox.showinfo('Aviso do Sistema', f'{os.path.basename(self.file)}\nfoi adicionado a sua playlist :)\n\nNa próxima vez que você iniciar o programa iremos reproduzir sua música') 

    def save_theme(self):
        selected = self.theme_value.get()
        selected_color = self.color_value.get()
        set_value = 'system'
        set_color = 'blue'

        if selected == 1:
            set_value = 'system'
        elif selected == 2:
            set_value = 'light'
        elif selected == 3:
            set_value = 'dark'

        if selected_color == 1:
            set_color = 'blue'
        elif selected_color == 2:
            set_color = 'dark-blue'
        elif selected_color == 3:
            set_color = 'green'

        settings.edit_ini('style', 'theme', str(set_value)) 
        settings.edit_ini('style', 'color', str(set_color))   
        answer = askyesno(title='Aviso do Sistema',
                        message=f'Suas preferências foram salvas com sucesso!\n\nO aplicativo precisa ser reniciado para aplicar as novas alterações\nDesejar reniciar agora?')
        if answer:
            os.execl(sys.executable, os.path.abspath(__file__), *sys.argv)
        else:
            messagebox.showinfo('Aviso do Sistema', 'As novas preferências serão exibidas no próximo login')

    def load_music_frame_musics(self):
        self.music_files = os.listdir(settings.folder_assets+'/audio/playlist/')

        self.selected = []

        for i in self.music_files:
            self.selected.append(i)

        position = 0

        for i in self.music_files:
            self.selected[position] = tkinter.IntVar()

            frame = ci.CTkFrame(self.music_frame, fg_color=("gray75", "gray30"), width=510, height=25)
            frame.propagate(0)
            frame.pack(pady=5)

            duration = MP3(settings.folder_assets+"/audio/playlist/"+i)
            duration = datetime.timedelta(seconds=duration.info.length)
            duration = f"{duration}".split('.')


            ci.CTkLabel(frame, text="♫", width=0, text_color=settings.hover_color, text_font=("Roboto Medium", -21)).pack(side="left", padx=10)
            name_frame = ci.CTkFrame(frame, height=30, width=360, fg_color=("gray75", "gray30"))
            name_frame.pack_propagate(0)
            name_frame.pack(side="left")

            if len(i) < 50:
                x = i.split('.mp3')[0]
                ci.CTkLabel(name_frame, text=x, width=0, text_font=(settings.code_injection['style']['font'], -14)).pack(side="left")
            else:
                x = i.split('.mp3')[0]
                ci.CTkLabel(name_frame, text=x[:50]+"...", width=0, text_font=(settings.code_injection['style']['font'], -14)).pack(side="left")

            ci.CTkLabel(frame, text=duration[0], text_font=(settings.code_injection['style']['font'], -14), width=0).pack(side="left", padx=10)
            
            delet=ci.CTkCheckBox(frame, text="", variable=self.selected[position])
            delet.pack(side="left", padx=10)
            
            ci.CTkFrame(self.music_frame, height=1, fg_color="gray45").pack(fill="both")

            position += 1

    def create_content(self):

        if settings.code_injection['style']['theme'] == 'dark':
            line_color = 'gray40'
        else:
            line_color = 'gray80'
            
        self.frame_content = ci.CTkFrame(self.master, corner_radius=0)
        self.frame_content.pack(padx=0)

        fetch = settings.c.execute("SELECT * FROM settings")
        rows = fetch.fetchone()

        try:
            scrollbar_style = Style()
            scrollbar_style.element_create("My.Vertical.Scrollbar.trough", "from", "default")
            scrollbar_style.layout('My.Vertical.TScrollbar', [('Vertical.Scrollbar.trough', {'children': [('Vertical.Scrollbar.thumb', {'expand': '1', 'sticky': 'nswe'})], 'sticky': 'ns'})])
            scrollbar_style.configure("My.Vertical.TScrollbar", scrollbar_style.configure("Vertical.TScrollbar"))
            if settings.code_injection['style']['theme'] == 'light':
                scrollbar_style.configure("My.Vertical.TScrollbar", gripcount=0, background="gray65", darkcolor="#DEDEDE", lightcolor="#DEDEDE", troughcolor="#DEDEDE", bordercolor="#DEDEDE", arrowcolor="#DEDEDE")
            else:
                scrollbar_style.configure("My.Vertical.TScrollbar", gripcount=0, background="gray35", darkcolor="#2E2E2E", lightcolor="#2E2E2E", troughcolor="#2E2E2E", bordercolor="#2E2E2E", arrowcolor="#2E2E2E")
        except:
            pass
        
        self.canvas = ci.CTkCanvas(self.frame_content, background=settings.bg_color, bd=0, highlightthickness=0, relief='ridge', width=650, height=600)
        scroll_y = ttk.Scrollbar(self.frame_content, orient="vertical", command=self.canvas.yview, style="My.Vertical.TScrollbar")

        self.frame = ci.CTkFrame(self.canvas, corner_radius=0, width=600, height=600)


        self.config = ci.CTkFrame(self.frame, fg_color=("gray75", "gray30"))
        self.config.grid(row=3, column=0, sticky="nswe", padx=10, pady=10)

        ci.CTkFrame(self.config, height=1, fg_color=None).pack(fill="both", pady=5)

        ci.CTkLabel(self.config, text="CONFIGURAÇÕES", text_font=("Roboto Medium", -22)).pack(pady=0)
        ci.CTkFrame(self.config, height=1, fg_color=line_color).pack(fill="both", pady=10)

        frame = ci.CTkFrame(self.config, fg_color=("gray75", "gray30"))
        frame.pack(fill="both")

        frame_switch = ci.CTkFrame(frame, fg_color=("gray75", "gray30"))
        frame_switch.pack(fill="both", padx=52)

        ci.CTkLabel(frame_switch, text="CRIAR PONTO DE RESTAURAÇÃO - INSTALAR APLICATIVOS: ", text_color=settings.hover_color, text_font=("Roboto Medium", -17)).pack(side="left")
        self.restore_apps = ci.CTkSwitch(frame_switch, text="\n", command=self.restore_apps)
        self.restore_apps.pack(side="left")




        frame_switch = ci.CTkFrame(frame, fg_color=("gray75", "gray30"))
        frame_switch.pack(fill="both", padx=52)
        ci.CTkLabel(frame_switch, text="CRIAR PONTO DE RESTAURAÇÃO - EXECUTAR FUNÇÕES: ", text_color=settings.hover_color, text_font=("Roboto Medium", -17)).pack(side="left")
        self.restore_function = ci.CTkSwitch(frame_switch, text="\n", command=self.restore_function)
        self.restore_function.pack(side="left")


        if settings.code_injection['app']['restore_point_apps'] == "true":
            self.restore_apps.select()
        if settings.code_injection['app']['restore_point_func'] == "true":
            self.restore_function.select()

        frame = ci.CTkFrame(self.config, height=5, fg_color=("gray75", "gray30"))
        frame.pack(fill="both", padx=5, pady=8)


        self.config = ci.CTkFrame(self.frame, fg_color=("gray75", "gray30"))
        self.config.grid(row=4, column=0, sticky="nswe", padx=10, pady=10)

        ci.CTkFrame(self.config, height=1, fg_color=None).pack(fill="both", pady=5)

        ci.CTkLabel(self.config, text="ESTILO", text_font=("Roboto Medium", -22)).pack(pady=0)
        ci.CTkFrame(self.config, height=1, fg_color=line_color).pack(fill="both", pady=10)


        frame = ci.CTkFrame(self.config, height=27, fg_color=("gray75", "gray30"))
        frame.pack(fill="both", padx=15, pady=10)

        ci.CTkLabel(frame, text="   TEMA:", text_color=settings.hover_color, text_font=("Roboto Medium", -17)).pack(side="left")
        self.theme_value = tkinter.IntVar()
        self.theme_system = ci.CTkRadioButton(frame, text="Sistema", value=1, variable=self.theme_value, text_font=(settings.code_injection['style']['font'], -16))
        self.theme_system.pack(side="left", padx=10)

        self.theme_light = ci.CTkRadioButton(frame, text="Claro", value=2, variable=self.theme_value, text_font=(settings.code_injection['style']['font'], -16))
        self.theme_light.pack(side="left", padx=20)

        self.theme_dark = ci.CTkRadioButton(frame, text="Escuro"+" "*42, value=3, variable=self.theme_value, text_font=(settings.code_injection['style']['font'], -16))
        self.theme_dark.pack(side="left")

        if settings.code_injection['style']['theme'] == "system":
            self.theme_system.select()
        elif settings.code_injection['style']['theme'] == "dark":
            self.theme_dark.select()
        elif settings.code_injection['style']['theme'] == "light":
            self.theme_light.select()

        ci.CTkFrame(self.config, height=1.2, fg_color=line_color).pack(fill="both", pady=10)
        frame = ci.CTkFrame(self.config, height=27, fg_color=("gray75", "gray30"))
        frame.pack(fill="both", padx=25, pady=10)

        ci.CTkLabel(frame, text="CORES:", text_color=settings.hover_color, text_font=("Roboto Medium", -17)).pack(side="left")
        self.color_value = tkinter.IntVar()
        self.color_blue = ci.CTkRadioButton(frame, text="Azul", value=1, variable=self.color_value, hover_color='#1fa6e8', text_font=(settings.code_injection['style']['font'], -16))
        self.color_blue.pack(side="left")

        self.color_darkblue = ci.CTkRadioButton(frame, text="Azul-Escuro", value=2, variable=self.color_value, hover_color='#608BD5', text_font=(settings.code_injection['style']['font'], -16))
        self.color_darkblue.pack(side="left", padx=25)

        self.color_green = ci.CTkRadioButton(frame, text="Verde", value=3, variable=self.color_value, hover_color='#72CF9F', text_font=(settings.code_injection['style']['font'], -16))
        self.color_green.pack(side="left")

        if settings.code_injection['style']['color'] == "blue":
            self.color_blue.select()
        elif settings.code_injection['style']['color'] == "green":
            self.color_green.select()
        elif settings.code_injection['style']['color'] == "dark-blue":
            self.color_darkblue.select()

        ci.CTkFrame(self.config, height=1.2, fg_color=line_color).pack(fill="both")
        
        ci.CTkButton(self.config, width=20, text='Salvar personalização', text_font=(settings.code_injection['style']['font'], -16), command=self.save_theme).pack(fill='both', pady=10, padx=20)
        ci.CTkFrame(self.config, height=1.2, fg_color=None).pack(fill="both")


        self.config = ci.CTkFrame(self.frame, fg_color=("gray75", "gray30"))
        self.config.grid(row=5, column=0, sticky="nswe", padx=10, pady=10)

        ci.CTkFrame(self.config, height=1, fg_color=None).pack(fill="both", pady=5)

        ci.CTkLabel(self.config, text="MÚSICA", text_font=("Roboto Medium", -22)).pack(pady=0)
        ci.CTkFrame(self.config, height=1, fg_color=line_color).pack(fill="both", pady=10)

        frame = ci.CTkFrame(self.config, fg_color=("gray75", "gray30"))
        frame.pack(fill="both")

        frame_switch = ci.CTkFrame(frame, fg_color=("gray75", "gray30"))
        frame_switch.pack(fill="both", padx=65)

        ci.CTkLabel(frame_switch, text="REPRODUZIR PLAYLIST AO INICIAR O PROGRAMA: ", text_color=settings.hover_color, text_font=("Roboto Medium", -17)).pack(side="left")
        self.playlist = ci.CTkSwitch(frame_switch, text="\n", command=self.background_music)
        self.playlist.pack(side="left")


        frame_switch = ci.CTkFrame(frame, fg_color=("gray75", "gray30"))
        frame_switch.pack(fill="both", padx=65)
        ci.CTkLabel(frame_switch, text="INICIAR O PROGRAMA COM A PLAYLIST PAUSADA: ", text_color=settings.hover_color, text_font=("Roboto Medium", -17)).pack(side="left")
        self.play_pause = ci.CTkSwitch(frame_switch, text="", command=self.play_pause)
        self.play_pause.pack(side="left")


        if settings.code_injection['playlist']['background_music'] == 'true':
            self.playlist.select()

        if settings.code_injection['playlist']['startup_music'] == 'pause':
            self.play_pause.select()

        frame = ci.CTkFrame(self.config, height=5, fg_color=("gray75", "gray30"))
        frame.pack(fill="both", padx=5, pady=8)

        frame = ci.CTkFrame(self.config, height=27, fg_color=("gray75", "gray30"))
        frame.pack(fill="both", padx=20, pady=8)

        ci.CTkLabel(frame, text=" "*10+"PLAYLIST"+" "*33, text_color=settings.hover_color, text_font=("Roboto Medium", -17)).pack(side="left", padx=15)
        ci.CTkButton(frame, text="Adicionar", corner_radius=8, fg_color=("gray80", "gray25"), text_font=(settings.code_injection['style']['font'], -13), command=self.add_music).pack(side="left", padx=10)
        ci.CTkButton(frame, text="Deletar", corner_radius=8, fg_color=("gray80", "gray25"), text_font=(settings.code_injection['style']['font'], -13), command=self.delet_music).pack(side="left")

        self.playlist_musics_frame = ci.CTkFrame(self.config, height=27, fg_color=("gray75", "gray30"))
        self.playlist_musics_frame.pack(fill="both", padx=10)

        self.music_frame = ci.CTkFrame(self.playlist_musics_frame, fg_color=("gray75", "gray30"))
        self.music_frame.pack()

        self.load_music_frame_musics()

        ci.CTkFrame(self.config, height=1.2, fg_color=None).pack(fill="both", pady=10)

        self.frame.bind("<Configure>", lambda event, canvas=self.canvas: self.onFrameConfigure(self.canvas))
        self.canvas.create_window(0, 0, anchor='nw', window=self.frame)
        self.canvas.update_idletasks()
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        self.canvas.configure(scrollregion=self.canvas.bbox('all'),yscrollcommand=scroll_y.set)                         
        self.canvas.pack(expand=True, side='left', pady=20)
        scroll_y.pack(fill='y', side='right',pady=20, padx=5)