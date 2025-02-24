import tkinter
from tkinter import messagebox, ttk
import customtkinter as ci
from PIL import Image, ImageTk
from app import settings
from app import data 
from datetime import datetime
from datetime import timedelta
from app import logs

class changelog(ci.CTkFrame):
    def __init__(self, master):
        self.master = master
        self.master.title(f'Changelog - {settings.app_name} v{settings.app_version}')
        self.master.iconbitmap(settings.folder_assets+"/img/code-injection.ico")
        self.master.focus_force()
        self.master.geometry("640x550+10+10")
        self.master.resizable(0,0)
        self.set_data = data.UserData()
        self.create_frames()
        self.create_labels()


    def close(self):
        self.master.destroy()

    def accept(self, event=None):
        if(self.value_checkbox.get() == 1):
            settings.edit_ini('app', 'hide_changelog', 'true')
        for i in self.master.winfo_children():
            i.destroy()
        self.master.login()  

    def create_frames(self): 
        self.frame = ci.CTkFrame(width=600, height=400)
        self.frame.pack(padx=40, pady=30)

        self.middle_frame = ci.CTkFrame(self.frame, width =564, height=500)
        self.middle_frame.propagate(0) 
        self.middle_frame.pack(fill='both', side='right', expand='False', padx=35, pady=10,)

        self.upper_frame = ci.CTkFrame(self.middle_frame, height = 50, width = 100) 
        self.upper_frame.propagate(0) 
        self.upper_frame.pack(fill='x', side='top', expand='False')

        self.bottom_frame = ci.CTkFrame(self.middle_frame, height = 90)
        self.bottom_frame.propagate(0) 
        self.bottom_frame.pack(fill='x', side='bottom', expand='False')
        self.master.bind('<Return>', self.accept)


    def create_labels(self):
        ci.CTkLabel(self.upper_frame, text="REGISTROS DE ALTERAÇÕES", text_font=(settings.code_injection['style']['font'], 19)).place(relx=0.17, rely=0.1)

        self.value_checkbox = tkinter.IntVar()
        self.checkbox = ci.CTkCheckBox(self.bottom_frame, variable=self.value_checkbox, text='Não mostrar isso novamente', onvalue=1, offvalue=0, text_font=(settings.code_injection['style']['font'], 11))
        self.checkbox.place(rely=0.45, relx=0)


        self.btn = ci.CTkButton(self.bottom_frame, text='Continuar', width=200, text_font=(settings.code_injection['style']['font'], 12), command=self.accept)
        self.btn.place(relx=0.58, rely=0.45)  
