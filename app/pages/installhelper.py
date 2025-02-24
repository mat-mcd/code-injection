import time, os, threading, subprocess, json
from playsound import playsound
from app import settings
import customtkinter as ci
from PIL import Image, ImageTk
import tkinter as tk
from app import logs
from pygame import mixer

class helper:
    def __init__(self, json_instance, programs_selected, page_instance):
        self.json_instance = json_instance
        self.programs_selected = programs_selected
        self.page_instance = page_instance
        self.commands_to_execute = []
        self.programs_to_execute = []
        self.select_deselect_all = 0
        self.select_deselect_basic = 0
        self.select_deselect_essential = 0
        self.is_running = False

    def start_installer(self, event=None):
        if self.is_running == True:
            pass
        else:
            self.is_running = True
            pr=threading.Thread(target=self.download)
            pr.start()

    def enable_scroll(self, event):
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    def download(self):
        i = 0
        while i < len(self.json_instance.json_keys):
            if self.get_button_status(i):
                self.commands_to_execute.append(self.json_instance.json_commands[i])
                self.programs_to_execute.append(self.json_instance.json_names[i])
            i+=1

        if(len(self.commands_to_execute)):
            self.update_label()
        else:
            self.page_instance.label_txt['text'] = "Por favor, selecione um aplicativo"
 
    def get_button_status(self, key):
        return self.programs_selected.programs_selected[key].get()

    def update_label(self):
        self.process_checker()
        settings.notification("Aplicativos Instalados", 15)
        self.is_running = False 
        self.page_instance.label_txt['text'] = "Aplicativos Instalados"

        try:
            mixer.init()
            self.driver_found = True
        except Exception as e:
            self.driver_found = False

        if self.driver_found:
            mixer.Channel(0).play(mixer.Sound(settings.folder_assets+"/audio/alerta.mp3"))
            time.sleep(1)
            mixer.Channel(0).play(mixer.Sound(settings.folder_assets+"/audio/aplicativos-instalados.mp3"))
            
        #self.page_instance.start.configure(state='active')

    def process_checker(self):
        bar_checker = 100/len(self.commands_to_execute)
        self.page_instance.progressbar.set(0)
        self.page_instance.pb["value"] = 0
        self.page_instance.pb.update()
        self.page_instance.progressbar.update()
        #self.page_instance.start.configure(state='disabled')

        if settings.code_injection['app']['restore_point_apps'] == "true":
            self.page_instance.label_txt['text'] = f"Criando ponto de restauração..."
            settings.terminal('REG ADD "HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\SystemRestore" /V "SystemRestorePointCreationFrequency" /T REG_DWORD /D 0 /F')
            settings.terminal('powershell.exe Checkpoint-Computer -Description "CodeInjection" -RestorePointType "MODIFY_SETTINGS"')
            
        list_selected = []
        for state in self.programs_selected.programs_selected:
            list_selected.append(state.get())
        cache = {
            "programs":list_selected
        }
        with open(settings.folder_assets+'/configs/programs_cache.json', 'w') as f:
            json.dump(cache, f)
        while(len(self.commands_to_execute) > 0):
            if settings.dev_mode == False:
                logs.add.insert_log(self, f"Instalou {self.programs_to_execute[0]}")
            self.page_instance.label_txt['text'] = f"Instalando {self.programs_to_execute[0]}..."
            self.page_instance.pb.update()
            self.page_instance.progressbar.update()
            try:
                subprocess.Popen("start /w "+self.commands_to_execute[0], shell=True, creationflags=settings.disable_terminal, startupinfo=settings.startupinfo).wait()
            except Exception as e:
                settings.notification(f"Falha ao instalar um aplicativo - {self.programs_to_execute[0]}\n\n{e}", 15) 

            self.page_instance.pb['value'] += bar_checker 
            new_progressbar = self.page_instance.pb['value'] / 100.0
            self.page_instance.progressbar.set(new_progressbar)

            del self.commands_to_execute[0]
            del self.programs_to_execute[0]
            self.page_instance.pb.update()
            self.page_instance.progressbar.update()
    
    #Split executable commands            
    def __split_commands(self, command):
        commands_splitted = []
        commands_splitted = command.split(' ')
        return commands_splitted

    def install_all_programs(self):
        file = open(settings.folder_assets+'/configs/programs_cache.json',"r+")
        file.truncate(0)
        file.close()
        i=0
        self.select_deselect_all += 1
        while i < len(self.programs_selected.programs_selected):
            self.programs_selected.programs_selected[i].set(0)
            if self.select_deselect_all % 2 == 0:
                self.programs_selected.programs_selected[i].set(0)
            else:
                self.programs_selected.programs_selected[i].set(1)
            i += 1
    
    def install_basic_programs(self):
        file = open(settings.folder_assets+'/configs/programs_cache.json',"r+")
        file.truncate(0)
        file.close()
        i=0
        self.select_deselect_basic += 1
        while i < len(self.json_instance.data):
            self.programs_selected.programs_selected[i].set(0)
            if(self.json_instance.json_keys[i] in self.programs_selected.basic_programs):
                if self.select_deselect_basic % 2 == 0:
                    self.programs_selected.programs_selected[i].set(0)
                else:
                    self.programs_selected.programs_selected[i].set(1)
            i += 1

    def install_essential_programs(self):
        file = open(settings.folder_assets+'/configs/programs_cache.json',"r+")
        file.truncate(0)
        file.close()
        i=0
        self.select_deselect_essential += 1
        while i < len(self.json_instance.data):
            self.programs_selected.programs_selected[i].set(0)
            if(self.json_instance.json_keys[i] in self.programs_selected.essential_programs):
                    if self.select_deselect_essential % 2 == 0:
                        self.programs_selected.programs_selected[i].set(0)
                    else:
                        self.programs_selected.programs_selected[i].set(1)
            i += 1