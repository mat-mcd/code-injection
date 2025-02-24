import tkinter
import customtkinter as ci
from tkinter import ttk
from app import settings
from app.pages.installhelper import helper
from app import jsonreader
from app.programs import programsvariables
from PIL import Image, ImageTk
from tkinter.ttk import * 

class InstallApps(ci.CTkFrame):
    def __init__(self, master, window):
        self.window = window
        self.master = master
        self.json_file = jsonreader.jsonhelper()
        self.programs_variables = programsvariables(len(self.json_file.json_keys))
        self.installer_helper = helper(self.json_file, self.programs_variables, self)
        self.create_frame()
        self.create_content()
        style = ttk.Style()
        style.theme_use("clam")
        self.window.unbind('<Return>')
        self.window.bind('<Return>', self.installer_helper.start_installer)

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    def create_frame(self):
        self.middle_frame = ci.CTkFrame(self.master)
        self.middle_frame.propagate(0) 
        self.middle_frame.pack(fill='both', side='right', expand='True', padx=20, pady=20)

        self.upper_frame = ci.CTkFrame(self.middle_frame, height = 50, width = 900) 
        self.upper_frame.propagate(0) 
        self.upper_frame.pack(fill='x', side='top', expand='False')

        self.bottom_frame = ci.CTkFrame(self.middle_frame, height = 60, width = 900)
        self.bottom_frame.propagate(0) 
        self.bottom_frame.pack(fill='x', side='bottom', expand='False')

        self.canvas = ci.CTkCanvas(self.middle_frame, background=settings.bg_color, bd=0, highlightthickness=0, relief='ridge')
        self.canvas.propagate(0) 
        self.canvas.pack(fill='both', expand=True, pady=0)

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

        self.v = ttk.Scrollbar(self.canvas, command=self.canvas.yview, style="My.Vertical.TScrollbar")
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

    def create_content(self):
        self.select_all = ci.CTkButton(self.upper_frame, text ="    Selecionar Todos    ", text_font=(settings.code_injection['style']['font'], 10), command =self.installer_helper.install_all_programs).place(relx=0, rely=0)
        self.select_essential = ci.CTkButton(self.upper_frame, text ="    Selecionar Essenciais    ", text_font=(settings.code_injection['style']['font'], 10), command =self.installer_helper.install_essential_programs).place(relx=0.37)

        self.select_basic = ci.CTkButton(self.upper_frame, text ="    Selecionar Básicos    ", text_font=(settings.code_injection['style']['font'], 10), command =self.installer_helper.install_basic_programs).place(relx=0.69)
        
        position = 0
        for program_element in self.json_file.json_keys:
            selected = self.programs_variables.programs_selected[position] == 1
            self.programs_variables.programs_selected[position] = tkinter.IntVar()

            img = ImageTk.PhotoImage(Image.open(settings.folder_assets+"/img/icons/programs/"+self.json_file.data[program_element]["icone"]))
            self.label = ci.CTkButton(self.canvas, image=img, text=self.json_file.data[program_element]["nome"]+" "*10, height=50, hover_color=None, text_font=(settings.code_injection['style']['font'], -17), border_width=0, fg_color=("#DEDEDE", "#2E2E2E"))
            self.label.grid(row=position, column=0, sticky=tkinter.W)

            
            self.canvas.create_window(15, (position+1)*30, anchor='nw', window=self.label, height=26)
            self.canvas.create_line(0, 26 + (position+1)*30, 620, 26 + (position+1)*30,fill=settings.line_color)
            self.checkButton = ci.CTkSwitch(self.canvas, text='', variable=self.programs_variables.programs_selected[position], bd=0)
            self.canvas.create_window(580, (position+1)*30, anchor='nw', window=self.checkButton, height=26)
            if(selected):
                self.programs_variables.programs_selected[position].set(1)

            position += 1
        
        self.canvas.configure(scrollregion=self.canvas.bbox('all'), yscrollcommand=self.v.set)
        self.v.pack(side= 'right', fill='y')



        
        self.label_txt = ci.CTkLabel(self.bottom_frame, text="", text_font=(settings.code_injection['style']['font'], 12))
        self.label_txt.place(rely=0.25)
        
        self.progressbar = ci.CTkProgressBar(master=self.bottom_frame, width=550, height=14)
        self.progressbar.place(relx=0, rely=0.70)
        self.progressbar.set(0)

        self.pb = ttk.Progressbar(master=self.bottom_frame)
        self.pb.place(relx=0, rely=5)
        self.pb['value'] = 0

        start_img = ImageTk.PhotoImage(Image.open(settings.folder_assets+f"/img/icons/{settings.icon_start}"))
        self.start = ci.CTkButton(master=self.bottom_frame, image=start_img, text='', hover_color=None, fg_color=("#DEDEDE", "#2E2E2E"), command=self.installer_helper.start_installer)
        self.start.place(relx=0.85, rely=0.23)
