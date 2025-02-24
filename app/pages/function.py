import tkinter, os, threading, time, urllib.request, psutil, cpuinfo, shutil, subprocess, pythoncom, wmi, json
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
from tkinter import PhotoImage
from tkinter import ttk
from pygame import mixer

class function(ci.CTkFrame):
    def __init__(self, master, window):
        self.window = window
        self.master = master
        self.is_running = False
        self.user_data = data.UserData.get_instance()
        self.selected = []
        self.__json_aux()
        self.__load_cache() 
        self.create_content()
        self.window.unbind('<Return>')
        self.window.bind('<Return>', self.__start_threading)   

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    def onFrameConfigure(self,canvas):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def __start_threading(self, event=None):
        if self.is_running == True:
            pass
        else:
            self.is_running = True
            sf=threading.Thread(target=self.__exec_functions)
            sf.start()

    def __json_aux(self):
        if settings.bits:
            self.json_file = open(settings.folder_assets+"/configs/functions_x64.json", encoding="utf8")
        else:
            self.json_file = open(settings.folder_assets+"/configs/functions_x32.json", encoding="utf8")
        self.data = json.load(self.json_file)
        self.keys = [keys for keys in self.data.keys()]
        self.functions = []
        for keys in self.keys:
            icon = self.data[keys]['icon']
            name = self.data[keys]['name']
            description = self.data[keys]['description']
            requirements = self.data[keys]['requirements']
            self.functions.append(f'{name}|{description}|{requirements}|{icon}')
            self.selected.append(keys)

    def __save_chache(self):
        cache = ""
        for i in range(len(self.selected)):
            cache = cache+f"{self.selected[i].get()},"
        settings.edit_ini('functions', 'cache', str(cache))


    def __load_cache(self):
        self.cache = settings.code_injection['functions']['cache']
        self.cache = self.cache.split(',')

    def __exec_functions(self):
        self.__save_chache()
        self.num_commands = 0
        self.pb["value"] = 0 
        self.progressbar.set(0)
        #self.start.configure(state='disabled')

        if settings.code_injection['app']['restore_point_func'] == "true":
            self.progressbar_text.configure(text= f"Criando ponto de restauração...")
            settings.terminal('REG ADD "HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\SystemRestore" /V "SystemRestorePointCreationFrequency" /T REG_DWORD /D 0 /F')
            settings.terminal('powershell.exe Checkpoint-Computer -Description "CodeInjection" -RestorePointType "MODIFY_SETTINGS"')


        for i in range(len(self.selected)):
            if self.selected[i].get() == 1:
                key = self.keys[i]
                commands = self.data[key]["comando"]
                for x in commands:
                    self.num_commands += 1

        for i in range(len(self.selected)):
            if self.selected[i].get() == 1:
                key = self.keys[i]
                name = self.data[key]["name"]
                commands = self.data[key]["comando"]
                self.progressbar_text.configure(text=f"Executando: {name}")
                
                bar_checker = 100/self.num_commands

                for c in commands:
                    self.pb['value'] += bar_checker 
                    new_progressbar = self.pb['value'] / 100.0 
                    self.progressbar.set(new_progressbar) 
                    if "SDI64-drv.exe" in c or "SDI32-drv.exe" in c:
                        os.system(c)
                    elif "windows-office.cmd" in c:
                        os.system(c)
                    else:
                        settings.terminal(c, True)

        settings.notification("Tarefas Finalizadas", 15)            
        self.start.configure(state='enabled')
        self.is_running = False              
        self.progressbar_text.configure(text="Tarefas Finalizadas")   

        try:
            mixer.init()
            self.driver_found = True
        except Exception as e:
            self.driver_found = False

        if self.driver_found:
            mixer.Channel(0).play(mixer.Sound(settings.folder_assets+"/audio/alerta.mp3"))
            time.sleep(1)
            mixer.Channel(0).play(mixer.Sound(settings.folder_assets+"/audio/tarefas-finalizadas.mp3"))



    def create_content(self):
        try:
            scrollbar_style = Style()
            scrollbar_style.element_create("My.Vertical.Scrollbar.trough", "from", "default")
            scrollbar_style.layout('My.Vertical.TScrollbar', [('Vertical.Scrollbar.trough', {'children': [('Vertical.Scrollbar.thumb', {'expand': '1', 'sticky': 'nswe'})], 'sticky': 'ns'})])
            scrollbar_style.configure("My.Vertical.TScrollbar", scrollbar_style.configure("Vertical.TScrollbar"))
            scrollbar_style.configure("My.Vertical.TScrollbar", gripcount=0, background="gray35", darkcolor="#2E2E2E", lightcolor="#2E2E2E", troughcolor="#2E2E2E", bordercolor="#2E2E2E", arrowcolor="#2E2E2E")
        except:
            pass

        self.canvas = ci.CTkCanvas(self.master, background=settings.bg_color, bd=0, highlightthickness=0, relief='ridge', width=650, height=520)
        scroll_y = ttk.Scrollbar(self.master, orient="vertical", command=self.canvas.yview, style="My.Vertical.TScrollbar")
        self.canvas.configure(scrollregion=self.canvas.bbox('all'),yscrollcommand=scroll_y.set) 
        scroll_y.pack(fill='y', side='right',pady=20, padx=15)

        self.frame = ci.CTkFrame(self.canvas, width=800, height=400)
        self.frame.pack(pady=25, fill='both')

        blank = ci.CTkFrame(self.frame, width=670, height=0)
        blank.pack()
        blank.propagate(0)

        start_img = ImageTk.PhotoImage(Image.open(settings.folder_assets+f"/img/icons/{settings.icon_start}"))
        self.start = ci.CTkButton(master=self.master, image=start_img, text='', width=35, hover_color=None, fg_color=("#DEDEDE", "#2E2E2E"), command=self.__start_threading)
        self.start.place(relx=0.855, rely=0.90)

        self.progressbar_text = ci.CTkLabel(master=self.master, text="", text_font=(settings.code_injection['style']['font'], -18))
        self.progressbar_text.place(rely=0.88, relx=0.05)

        self.progressbar = ci.CTkProgressBar(master=self.master, width=520, height=14)
        self.progressbar.place(rely=0.93, relx=0.06)
        self.progressbar.set(0)

        self.pb = ttk.Progressbar(master=self.master, length=500, orient='horizontal')
        self.pb.place(relx=0.1, rely=3)
        self.pb['value'] = 0

        position = 0

        for i in self.functions:
            self.selected[position] = tkinter.IntVar()

            i = i.split('|')

            frame = ci.CTkFrame(self.frame)
            frame.pack(fill="both", pady=10, padx=25)

            left_frame = ci.CTkFrame(frame, height=0)
            left_frame.pack(fill="both", side=tkinter.LEFT)
            right_frame = ci.CTkFrame(frame, height=0)
            right_frame.pack(fill="both", side=tkinter.RIGHT)
            top_frame = ci.CTkFrame(left_frame, height=0)
            top_frame.pack(fill="both")
            under_frame = ci.CTkFrame(left_frame, height=0)
            under_frame.pack(fill="both")
            requirements_frame = ci.CTkFrame(under_frame, height=0)
            requirements_frame.grid(row=1, column=1, padx=47, sticky="nswe", pady=5)
            description_frame = ci.CTkFrame(under_frame, height=0)
            description_frame.grid(row=0, column=1, padx=47, sticky="nswe")

            img_file = PhotoImage(file=settings.folder_assets+i[3])
            functionimg = ci.CTkLabel(top_frame, image=img_file, width=30)
            functionimg.grid(row=0, column=0)
            functionimg.image = img_file

            requirements = i[2].replace('[', '').replace(']', '').replace("'", "")
            requirements = requirements.split(',')

            description = i[1].split('\r')
            if description[0] == "":
                description_frame.destroy()
            else:
                for x in description:
                    ci.CTkLabel(description_frame, text=x, width=10, text_font=(settings.code_injection['style']['font'], 12)).grid(sticky="nswe")

            name = ci.CTkLabel(top_frame, text=i[0], width=10, text_color=settings.hover_color, text_font=(settings.code_injection['style']['font'], 13)).grid(row=0, column=1)
            checkbox = ci.CTkCheckBox(right_frame, text="", variable=self.selected[position]).pack(side=tkinter.RIGHT, padx=7)
            line = ci.CTkFrame(self.frame, height=1, fg_color=("gray75", "gray30")).pack(fill="both", padx=30, pady=3)

            if self.cache[position] == "1":
                self.selected[position].set(1)

            if requirements[0] == "":
                requirements_frame.destroy()
            else:
                for x in requirements:
                    ci.CTkLabel(requirements_frame, text="  "+x+"  ", height=1, width=1, fg_color=("gray75", "gray30"), text_font=(settings.code_injection['style']['font'], 11)).pack(side=tkinter.LEFT, padx=3)

            position += 1

        self.frame.bind("<Configure>", lambda event, canvas=self.canvas: self.onFrameConfigure(self.canvas))
        self.canvas.create_window(0, 0, anchor='nw', window=self.frame)
        self.canvas.update_idletasks()
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        self.canvas.configure(scrollregion=self.canvas.bbox('all'),yscrollcommand=scroll_y.set)                         
        self.canvas.pack(expand=True, side='left', pady=25)
        self.canvas.place(x=0, y=15)




       