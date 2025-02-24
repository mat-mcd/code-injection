import tkinter, os, threading, time, urllib.request, psutil, cpuinfo, shutil, subprocess, pythoncom, wmi
import customtkinter as ci
from tkinter import ttk
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

class logs(ci.CTkFrame):
    def __init__(self, master):
        self.master = master
        self.user_data = data.UserData.get_instance()
        self.create_content()


    def on_tree_select(self, event):
        for item in self.tree.selection():
            item_text = self.tree.item(item,"text")
            logs = settings.c.execute(f"SELECT * FROM logs WHERE id = '{item_text}'")
            rows = logs.fetchall()
            if (len(rows) > 0):
                for row in rows:
                    messagebox.showinfo(f"Detalhes da Ação - #{row[0]}", f"Indetificação: {row[0]}\nAção: {row[2]}\nUsuário: {row[1]}\nData: {row[3]}\n\n\nSerial HD: {row[4]}\nUsuário Windows: {row[5]}\nNome Computador: {row[6]}\nSistema: {row[7]}")
            else:
                messagebox.showerror("Detalhes da ação", "Ocorreu um erro ao recuperar informações sobre essa ação")



    def create_content(self):
        self.frame = ci.CTkFrame(self.master, width=800, height=600)
        self.frame.pack(pady=20, fill='both')

        self.frame2 = ci.CTkFrame(self.frame, width=500, height=50)
        self.frame2.pack(pady=0)

        self.page = ci.CTkLabel(self.frame, text="HISTÓRICO DE AÇÕES", text_font=("Roboto Medium", 20))
        self.page.place(relx=0.30, rely=0.01)
        self.subpage = ci.CTkLabel(self.frame, text="Clique na ação para visualizar detalhes", text_font=(settings.code_injection['style']['font'], 12))
        self.subpage.place(relx=0.305, rely=0.065)




        self.middle_frame = ci.CTkFrame(self.frame, width = 600, height=400)
        self.middle_frame.propagate(0) 
        self.middle_frame.pack(fill='both', expand='False', padx=50, pady=20)

        columns = ('acao', 'data')
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", width=10, foreground=settings.text_color, highlightthickness=1, bd=0, background=settings.bg_color, font=(settings.code_injection['style']['font'], 12))
        style.configure("Treeview.Heading",borderwidth=0, background=settings.font_color, foreground=settings.text_color, font=(settings.code_injection['style']['font'], 12,'bold')) 
        style.layout("Treeview", [('Treeview.treearea', {'sticky': 'nswe'})])
        self.tree = ttk.Treeview(self.middle_frame,columns=columns,show='headings',height='18')
        self.tree.place(relx=0, rely=0.01)
        self.tree.heading('acao', text = ' AÇÃO', anchor = 'w')
        self.tree.heading('data', text = 'DATA', anchor = 'center')
        self.tree.column('acao', width=370, anchor='w')
        self.tree.column('data', width=200, anchor='center')
        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)

        self.list_logging()
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
        treeScroll = ttk.Scrollbar(self.middle_frame, style="My.Vertical.TScrollbar")
        treeScroll.configure(command=self.tree.yview)
        self.tree.configure(yscrollcommand=treeScroll.set)
        treeScroll.pack(side=tkinter.RIGHT, fill=tkinter.BOTH)


        self.frame3 = ci.CTkFrame(self.frame, width=600, height=550)
        self.frame3.pack(pady=0)


        ci.CTkLabel(self.frame3, text="Pesquisar:      ", text_font=(settings.code_injection['style']['font'],12)).place(relx=0, rely=0)

        value_username = tkinter.StringVar(self.frame3)
        self.button_search = ci.CTkEntry(master=self.frame3, corner_radius=10, textvariable=value_username, width=500, height=35, placeholder_text="Pesquise por Ação, Data, Informações do OS, etc...")
        self.button_search.place(x=3,y=30)

        #button pesquisar
        img_download = PhotoImage(file=settings.folder_assets+"/img/icons/search.png")
        self.download_button = ci.CTkButton(self.frame3, width=50, image=img_download, cursor="hand2", text='', hover_color=None, fg_color=("#DEDEDE", "#2E2E2E"), command=self.search_event)
        self.download_button.image = img_download
        self.download_button.place(relx=0.88, rely=0.22)   


    def list_logging(self):
        records = self.tree.get_children()
        for element in records:
            self.tree.delete(element)        

        logs = settings.c.execute("SELECT * FROM logs ORDER BY id ASC")
        rows = logs.fetchall()
        if (len(rows) > 0):
                for row in rows:
                    self.tree.insert('', 0, text=row[0], values = (row[2],row[3]))


    def p(self):
        return self.button_search.get()


    def search_event(self):  
        for element in self.tree.get_children():
            self.tree.delete(element)

        logs = settings.c.execute("SELECT * FROM logs WHERE action LIKE '%"+self.button_search.get()+"%' OR user LIKE '%"+self.button_search.get()+"%' OR date LIKE '%"+self.button_search.get()+"%' OR serial_hd LIKE '%"+self.button_search.get()+"%' OR pc_username LIKE '%"+self.button_search.get()+"%' OR pc_name LIKE '%"+self.button_search.get()+"%' OR pc_system LIKE '%"+self.button_search.get()+"%' ORDER BY id ASC")
        rows = logs.fetchall()
        if (len(rows) > 0):
                for row in rows:
                    self.tree.insert('', 0, text = row[0], values = (row[2],row[3]))
        else:
            self.tree.insert('', 0, text='Nenhum resultado encontrado', values = ("Nenhum resultado encontrado","--"))