import tkinter, datetime, threading, psutil, sys, subprocess, wmi, cpuinfo, GPUtil, socket, requests, os
from tkinter import ttk
import soundcard as sc
import customtkinter as ci
from app import settings
from PIL import Image, ImageTk
from psutil._common import bytes2human
from screeninfo import get_monitors
from tkinter import messagebox
from tkinter.messagebox import askyesno
from app import data
from importlib import reload
from tkinter.ttk import *
                                     
class SysInfo(ci.CTkFrame):
    def __init__(self, master):
        self.master = master
        style = ttk.Style()
        style.theme_use("clam")
        style.configure('TFrame', background = 'red', foreground = 'red', width = 20, borderwidth=1, focusthickness=3, focuscolor='none')
        style.map('TFrame', background=[('active','red')])
        self.create_content()
        self.os_expanded_check = 0
        self.cpu_expanded_check = 0
        self.mobo_expanded_check = 0
        self.network_expanded_check = 0

        if settings.code_injection['app']['new_acess'] == "true":
            settings.notification(f'Bem-vindo ao {settings.app_name} v{settings.app_version}', 15)
            settings.edit_ini('app', 'new_acess', "false")
            reload(settings)

    def update_check(self):
        if settings.check_network():
            try:
                r = requests.post(settings.url_check_license+'update.php')
                result = r.json()          
                if settings.app_version < result['version']:

                    answer = askyesno(title='Nova atualização encontrada', message='Uma nova versão está disponível para download\nVersão Atual: '+settings.app_version+'\nNova versão: '+result['version']+'\n\nDesejar atualizar?')
                    if answer:
                        subprocess.Popen([settings.folder_assets+'/update.exe', settings.folder_assets], startupinfo=settings.startupinfo, creationflags=settings.disable_terminal)
                        sys.exit(1)    

            except Exception as e:
                settings.notification(f'Erro ao conectar ao servidor de atualização', 15)



    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    
    def usage_or_temperature(self, value):
        if int(value) >= 70:
            color = '#f91111'
        elif int(value) >= 50:
            color = '#e2d009'
        elif int(value) <= 50:
            color = '#0E9670'
        else:
            color = '#fff'
        return color

    def dashboard(self):
        cpu = subprocess.Popen('wmic cpu get Name', shell=True, stdout=subprocess.PIPE, startupinfo=settings.startupinfo, creationflags=settings.disable_terminal) 
        data = cpu.stdout.read().decode('cp850')
        data = data.replace('  ', '').strip().split('\n')        
        self.cpu_result.configure(text=str(data[1]), padx=35) 

        try:
            import pythoncom
            pythoncom.CoInitialize()
            c = wmi.WMI()    
            systeminfo = c.Win32_ComputerSystem()[0]
            motherboard = str(systeminfo.Manufacturer.replace('  ', '')+' - '+systeminfo.Model.replace('  ', ''))
            self.mobo_result.configure(text=motherboard, width=0, padx=65)
        except Exception as e:
            self.mobo_result.configure(text="--")
        

        self.ram_result = ci.CTkFrame(self.frame, fg_color=("#DEDEDE", "#2E2E2E"))

        try:
            memorys = []
            memory_data = subprocess.Popen('Powershell.exe try{(Get-CimInstance win32_physicalmemory)}Catch{(Get-WmiObject win32_physicalmemory)}', stdin=subprocess.PIPE, creationflags=settings.disable_terminal, stdout=subprocess.PIPE, stderr=subprocess.PIPE, startupinfo=settings.startupinfo, encoding="cp850")
            memory_data, error = memory_data.communicate()
            memory_data = memory_data.strip("\n").replace(" ", "").split('\n\n')
            for memory in memory_data:
                memory = memory.split('\n')
                capacity = ""
                memorytype = ""
                speed = ""
                manufacturer = ""
                devicelocator = ""
                for i in memory:
                    if 'Capacity' in i:
                        capacity = i.split(':')[1]
                        capacity = bytes2human(int(capacity)).split('.')[0]
                    if 'MemoryType' in i and not 'SMBIOS' in i:
                        memorytype = int(i.split(':')[1])
                        if memorytype == 20:
                            memorytype = "DDR"
                        elif memorytype == 21 or memorytype == 22 or memorytype == 23:
                            memorytype = "DDR2"
                        elif memorytype == 24:
                            memorytype = "DDR3"
                        elif memorytype == 26 or memorytype == 0:
                            memorytype = "DDR4"
                    if 'Speed' in i and not 'ConfiguredClock' in i:
                        speed = i.split(':')[1]
                    if 'Manufacturer' in i:
                        manufacturer = i.split(':')[1]
                        try:
                            if int(manufacturer) or int(manufacturer) == 0:
                                manufacturer = ""
                        except:
                            manufacturer = manufacturer+" "
                    if 'DeviceLocator' in i:
                        devicelocator = i.split(':')[1]
                memorys.append(f'{manufacturer}{capacity}GB {memorytype} {speed}Mhz - {devicelocator}')
            for memory in memorys:
                ci.CTkLabel(self.ram_result, text=memory, text_font=(settings.code_injection['style']['font'], 13)).grid(sticky=tkinter.W)
        except Exception as e:
            ci.CTkLabel(self.ram_result, text="--", text_font=(settings.code_injection['style']['font'], 13)).grid(sticky=tkinter.W)

        self.ram_result_main.destroy()
        self.ram_result.grid(row=14, column=0, sticky=tkinter.W, padx=90, pady=0)

        try:
            gpus = GPUtil.getGPUs()
            if not gpus:
                gpu = subprocess.Popen('wmic path win32_VideoController get name', stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, startupinfo=settings.startupinfo, creationflags=settings.disable_terminal, encoding="utf-8")
                gpu, error = gpu.communicate()
                gpu = gpu.replace('\n', '').replace('  ', '').replace('Name', '')
                self.gpu_result.configure(text=gpu)
            else:
                self.gpu_result.destroy()
                self.gpu_frame = ci.CTkFrame(self.frame)
                self.gpu_frame.grid(row=17, column=0, sticky=tkinter.W, padx=35)
 
                x = 1 
                for gpu_ in gpus:
                    total = str(gpu_.memoryTotal)
                    if "." in total:
                        size_gpu = total.split(".")[0]
                        if size_gpu < "1000.0":
                            size = 'MB' 
                        else:
                            size = 'GB'
                        size_gpu = size_gpu+ f'{size}'
                    else:
                        size_gpu = gpu_.memoryTotal

                    color = self.usage_or_temperature(gpu_.temperature)    
                    self.var1=ci.CTkLabel(self.gpu_frame, text=f'{gpu_.name} {size_gpu}', text_font=(settings.code_injection['style']['font'], 13)).grid(row=x, column=0, sticky=tkinter.W, padx=55, pady=0)    
                    self.var2=ci.CTkLabel(self.gpu_frame, text=f"{gpu_.temperature} °C", text_color=color, text_font=(settings.code_injection['style']['font'], 12)).grid(row=x, column=0, sticky=tkinter.W, padx=480, pady=0) 
                    x+=1
            try:        
                self.var1.destroy()
                self.var2.destroy()
            except:
                pass        
        except Exception as e:
            pass

        l = 1
        self.monitor_result.destroy()
        self.monitor_result = ci.CTkFrame(self.frame, fg_color=("#DEDEDE", "#2E2E2E"))
        self.monitor_result.grid(row=24, column=0, sticky=tkinter.W, padx=90, pady=0)
        for i in get_monitors():
            is_primary = i.is_primary
            monitor = f"Monitor {l} - {i.width}x{i.height}"
            if is_primary:
                monitor = monitor + " (Primário)"
            ci.CTkLabel(self.monitor_result, text=monitor, text_font=(settings.code_injection['style']['font'], 13)).grid(sticky=tkinter.W, padx=1)
            l += 1

        self.network_result.destroy()
        self.network_result = ci.CTkFrame(self.frame, fg_color=("#DEDEDE", "#2E2E2E"))
        self.network_result.grid(row=32, column=0, sticky=tkinter.W, padx=60, pady=0)
        net_io = psutil.net_io_counters()

        if settings.check_network():
            self.network_status = ci.CTkLabel(self.network_result, text="Conexão Internet: Conectado", text_font=(settings.code_injection['style']['font'], 13))
            self.network_status.grid(sticky=tkinter.W, padx=26)
        else:
            self.network_status = ci.CTkLabel(self.network_result, text="Conexão Internet: Desconectado", text_font=(settings.code_injection['style']['font'], 13))
            self.network_status.grid(sticky=tkinter.W, padx=26)

        self.sended_bytes = ci.CTkLabel(self.network_result, text=f"Bytes enviados: {bytes2human(net_io.bytes_sent)}", text_font=(settings.code_injection['style']['font'], 13))
        self.sended_bytes.grid(sticky=tkinter.W, padx=4)
        self.recived_bytes = ci.CTkLabel(self.network_result, text=f"Bytes recebidos: {bytes2human(net_io.bytes_recv)}", text_font=(settings.code_injection['style']['font'], 13))
        self.recived_bytes.grid(sticky=tkinter.W, padx=4)
        
        self.license_result.destroy()
        self.license_result = ci.CTkFrame(self.frame, fg_color=("#DEDEDE", "#2E2E2E"), height=15)
        self.license_result.grid(row=38, column=0, sticky=tkinter.W, padx=90, pady=0)
        windows_license = subprocess.Popen(r'cscript C:\Windows\System32\slmgr.vbs /xpr', shell=True, startupinfo=settings.startupinfo, stdout=subprocess.PIPE, creationflags=settings.disable_terminal)
        windows_license = windows_license.stdout.read()
        try:
            windows_license = windows_license.decode('cp850')
        except:
            pass
        win_status = 'Não foi possível coletar a informação'
        if "The machine is permanently activated" in windows_license:
            win_status = 'Ativado permanentemente'
        elif "otification mode" in windows_license:
            win_status = 'Modo de Notificação'
        elif "will expire" in windows_license:
            win_status = windows_license.replace('Volume activation will expire ', '').replace('\n', '').replace('  ','')
            win_status = 'Ativado até '+win_status.split(":",1)[1].lstrip().rstrip()
        elif "ativada permanentemente" in windows_license:
            win_status = 'Ativado permanentemente'
        elif "notificação" in windows_license:
            win_status = 'Modo de Notificação'
        elif "vencerá em" in windows_license:
            win_status = windows_license.replace('A ativação do volume vencerá em ', '').replace('\n', '').replace('  ','')
            win_status = 'Ativado até '+win_status.split(":",1)[1].lstrip().rstrip()
        ci.CTkLabel(self.license_result, text=f'Microsoft Windows - {win_status}', text_font=(settings.code_injection['style']['font'], 13)).grid(sticky=tkinter.W)
        
        from app import getprogramsinstalled
        y = ['2003', '2007', '2010', '2013', '365', '2016', '2019']
        x = getprogramsinstalled.programs_installed_array
        installed = []
        v = ""
        for i in y:
            for software in getprogramsinstalled.software_list:
                if 'Microsoft Office' in software['name'] and i in software['name']:
                    if not f'Microsoft Office {i}' in installed:                
                        installed.append(f'Microsoft Office {i}')
                        v = 16
                        if i == '2003':
                            v = 11
                        elif i == '2007':
                            v = 12 
                        elif i == '2010':
                            v = 14
                        elif i == '2013':
                            v = 15
                        if settings.bits:
                            folder = f'C:\\Program Files (x86)\\Microsoft Office\\Office{v}\\ospp.vbs'
                        else:
                            folder = f'C:\\Program Files\\Microsoft Office\\Office{v}\\ospp.vbs'
                        CMD = subprocess.Popen(f'cscript "{folder}" /dstatus', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE, startupinfo=settings.startupinfo, creationflags=settings.disable_terminal)
                        a = CMD.stdout.read()    
                        a = str(a).replace('\\r', '').split('\\n')
                        c = ''
                        for x in a:
                            if 'REMAINING GRACE:' in x:
                                c+= x.split(':')[1].split('(')[0].replace('  ', ' ')
                                c = c.replace('days', 'dias').replace('minutes', 'minutos')
                                c = f'({c})'
                        for x in a:
                            if 'LICENSE STATUS:' in x:
                                b = a[a.index(x)].split(':')[1].replace(' ', '')
                                if b == '---LICENSED---':
                                    b = f'Ativado {c}'
                                else:
                                    b = f'Não ativado'
                        try:            
                            ci.CTkLabel(self.license_result, text=f'Microsoft Office {i} - {b}', text_font=(settings.code_injection['style']['font'], 13)).grid(sticky=tkinter.W)                        
                        except:
                            pass

        self.audio_result.destroy()
        self.audio_result = ci.CTkFrame(self.frame, fg_color=("#DEDEDE", "#2E2E2E"))
        self.audio_result.grid(row=28, column=0, sticky=tkinter.W, padx=90, pady=0)

        ci.CTkLabel(self.audio_result, text="Saida:", text_color=settings.hover_color, text_font=(settings.code_injection['style']['font'], 13), width=15).grid(sticky=tkinter.W)

        default_speaker = sc.default_speaker()
        default_mic = sc.default_microphone()
        speakers = sc.all_speakers()
        mics = sc.all_microphones()
        output = []
        input=[]

        for speakers in speakers:
            speaker = str(speakers)
            speaker = speaker.replace('<', '').replace('>', '')
            for i in range(10):
                try:
                    speaker = speaker.replace(f'({i} channels)', '')
                except:
                    pass
            if str(speakers) == str(default_speaker):
                speaker = speaker+"(Padrão)"
            if not speaker in output:
                output.append(speaker)

        for i in output:
            ci.CTkLabel(self.audio_result, text=i, text_font=(settings.code_injection['style']['font'], 13)).grid(padx=20, sticky=tkinter.W)

        ci.CTkLabel(self.audio_result, text="Entrada:", text_color=settings.hover_color, text_font=(settings.code_injection['style']['font'], 13), width=15).grid(sticky=tkinter.W)
        
        for mics in mics:
            mic = str(mics).replace('<', '').replace('>', '')
            for i in range(10):
                try:
                    mic = mic.replace(f'({i} channels)', '')
                except:
                    pass
            if str(mics) == str(default_mic):
                mic = mic+"(Padrão)"
            if not mic in input:
                input.append(mic)

        for i in input:
            ci.CTkLabel(self.audio_result, text=i, text_font=(settings.code_injection['style']['font'], 13)).grid(padx=20, sticky=tkinter.W)


        self.storage_result = ci.CTkFrame(self.frame, fg_color=("#DEDEDE", "#2E2E2E"))

        ci.CTkLabel(self.storage_result, text="Dispositivos:", text_color=settings.hover_color, text_font=(settings.code_injection['style']['font'], 13)).grid(sticky=tkinter.W)

        try:
            disks = subprocess.Popen('Powershell.exe Get-Disk | Format-List -Property Model, Size, HealthStatus', stdin=subprocess.PIPE, creationflags=settings.disable_terminal, stdout=subprocess.PIPE, stderr=subprocess.PIPE, startupinfo=settings.startupinfo, encoding="cp850")
            disks, error = disks.communicate()
            disks = disks.strip("\n").split('\n\n')
            disk = []
            for i in disks:
                i = i.split('\n')
                model = ""
                size = ""
                status = ""
                for x in i:
                    if "Model" in x:
                        model = x.split(':')[1].strip()
                    if "Size" in x:
                        size = x.split(':')[1].strip()
                    if "HealthStatus" in x:
                        status = x.split(':')[1].strip()
                disk.append([f'{model}', f'{size}', f'{status}'])
            for i in disk:
                frame = ci.CTkFrame(self.storage_result)
                frame.grid(padx=30, sticky=tkinter.W)
                text_frame = ci.CTkFrame(frame, width=325, height=20)
                text_frame.grid(row=0, column=0)
                text_frame.propagate(0)
                ci.CTkLabel(text_frame, text=f"{i[0]} - {bytes2human(int(i[1]))}", text_font=(settings.code_injection['style']['font'], 13)).pack(side="left")
                if i[2] == "Healthy":
                    ci.CTkLabel(frame, text=f"● Saudável", text_color="#0E9670", text_font=(settings.code_injection['style']['font'], 13)).grid(row=0, column=1)
                elif i[2] == "Unhealthy":
                    ci.CTkLabel(frame, text=f"● Pouco saudável", text_color="#f2df0c", text_font=(settings.code_injection['style']['font'], 13)).grid(row=0, column=1)
                elif i[2] == "Unknown":
                    ci.CTkLabel(frame, text=f"● Desconhecido", text_color="#adadad", text_font=(settings.code_injection['style']['font'], 13)).grid(row=0, column=1)
                elif i[2] == "Warning":
                    ci.CTkLabel(frame, text=f"● Critico", text_color="#ff0000", text_font=(settings.code_injection['style']['font'], 13)).grid(row=0, column=1)
        except Exception as e:
            print(e)
            disks = subprocess.Popen('wmic diskdrive get model,size', stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, startupinfo=settings.startupinfo, creationflags=settings.disable_terminal)
            disks = settings.filter(disks)
            for i in disks:
                frame = ci.CTkFrame(self.storage_result)
                frame.grid(padx=30, sticky=tkinter.W)
                ci.CTkLabel(frame, text=f"{i[0]} - {bytes2human(int(i[1]))}", text_font=(settings.code_injection['style']['font'], 13)).pack(fill="both", side="left")

        partitions = psutil.disk_partitions()
        ci.CTkLabel(self.storage_result, text=" Partições:", text_color=settings.hover_color, text_font=(settings.code_injection['style']['font'], 13), width=25).grid(sticky=tkinter.W)
        for disk in partitions:
            try:
                disk_usage = psutil.disk_usage(disk.mountpoint)
            except:
                pass
            disk = f"{disk.device} ({disk.fstype}) - Total: {bytes2human(disk_usage.total)} / Usado: {bytes2human(disk_usage.used)} / Livre: {bytes2human(disk_usage.free)}"
            ci.CTkLabel(self.storage_result, text=disk, text_font=(settings.code_injection['style']['font'], 13)).grid(padx=30, sticky=tkinter.W)
        self.storage_result_main.destroy()    
        self.storage_result.grid(row=21, column=0, sticky=tkinter.W, padx=90, pady=0)

    def update_loop(self):
        try:
            net_io = psutil.net_io_counters()
            self.sended_bytes.configure(text=f"Bytes enviados: {bytes2human(net_io.bytes_sent)}")
            self.recived_bytes.configure(text=f"Bytes recebidos: {bytes2human(net_io.bytes_recv)}")
        except:
            pass

        memory = psutil.virtual_memory()[2]
        color = self.usage_or_temperature(memory)
        self.ram_usage.configure(text=f"{memory}%", text_color=color)

        cpu = psutil.cpu_percent()
        color = self.usage_or_temperature(cpu)
        self.cpu_usage.configure(text=f"{cpu}%", text_color=color)

        self.master.after(1000, self.update_loop)

    def thread_os(self):
        try:
            if "Windows 7" in settings.system:
                key_reg = 'CurrentVersion'
            else:
                key_reg = 'DisplayVersion'
                
            domain = subprocess.Popen('Powershell.exe try{(Get-CimInstance Win32_ComputerSystem).Domain}Catch{(Get-WmiObject Win32_ComputerSystem).Domain}', stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,startupinfo=settings.startupinfo, creationflags=settings.disable_terminal, encoding="utf-8")
            domain, error = domain.communicate()
            domain = domain.replace('\n', '')
            result = subprocess.run("bcdedit", capture_output=True, text=True, startupinfo=settings.startupinfo, creationflags=settings.disable_terminal).stdout
            if 'winload.exe' in result:
                boot_mode = 'BIOS (Legacy)'
            elif 'winload.efi' in result:
                boot_mode = 'UEFI'
            else:
                boot_mode = 'Desconhecido'

            uptime = datetime.datetime.fromtimestamp(psutil.boot_time())
            uptime = uptime.strftime("%d/%m/%Y %H:%M:%S")
            self.os_thread_wait.destroy()
            ci.CTkLabel(self.os_expanded, text='Versão: '+str(settings.regedit("SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion", key_reg)), fg_color=("#DEDEDE", "#2E2E2E"), text_font=(settings.code_injection['style']['font'], 13)).grid(sticky=tkinter.W)
            ci.CTkLabel(self.os_expanded, text='Build: '+str(sys.getwindowsversion()[2]), fg_color=("#DEDEDE", "#2E2E2E"), text_font=(settings.code_injection['style']['font'], 13)).grid(sticky=tkinter.W)
            if str(settings.regedit("SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion",'ReleaseId')) != '--':
                ci.CTkLabel(self.os_expanded, text='ReleaseId: '+str(settings.regedit("SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion",'ReleaseId')), fg_color=("#DEDEDE", "#2E2E2E"), text_font=(settings.code_injection['style']['font'], 13)).grid(sticky=tkinter.W)
            ci.CTkLabel(self.os_expanded, text='Modo de Inicialização: '+str(boot_mode), fg_color=("#DEDEDE", "#2E2E2E"), text_font=(settings.code_injection['style']['font'], 13)).grid(sticky=tkinter.W)
            ci.CTkLabel(self.os_expanded, text='Data Últ. Inicialização: '+str(uptime), fg_color=("#DEDEDE", "#2E2E2E"), text_font=(settings.code_injection['style']['font'], 13)).grid(sticky=tkinter.W)
            ci.CTkLabel(self.os_expanded, text='Data de Instalação: '+str(settings.os_date_install), fg_color=("#DEDEDE", "#2E2E2E"), text_font=(settings.code_injection['style']['font'], 13)).grid(sticky=tkinter.W)
            ci.CTkLabel(self.os_expanded, text=f'Nome do Computador: {settings.pc_name}', fg_color=("#DEDEDE", "#2E2E2E"), text_font=(settings.code_injection['style']['font'], 13)).grid(sticky=tkinter.W)
            ci.CTkLabel(self.os_expanded, text=f'Nome de Usuário: {settings.pc_username}', fg_color=("#DEDEDE", "#2E2E2E"), text_font=(settings.code_injection['style']['font'], 13)).grid(sticky=tkinter.W)
            ci.CTkLabel(self.os_expanded, text=f'Grupo/Domínio: {domain}', fg_color=("#DEDEDE", "#2E2E2E"), text_font=(settings.code_injection['style']['font'], 13)).grid(sticky=tkinter.W)
        except Exception as x:
            messagebox.showerror('Aviso do Sistema', f'Falha ao obter dados do dispotivio\n\n{x}')


    def os_expanded(self):
        if self.os_expanded_check == 1:
            self.os_expanded.destroy()
            self.os_txt.configure(text='Sistema Operacional (+)')
            self.os_expanded_check = 0
        else:
            self.os_expanded = ci.CTkFrame(self.frame, fg_color=("#DEDEDE", "#2E2E2E"), height=15)
            self.os_expanded.grid(row=3, column=0, sticky=tkinter.W, padx=90, pady=0)
            self.os_thread_wait = ci.CTkLabel(self.os_expanded, text="coletando informações...", text_font=(settings.code_injection['style']['font'], 13), fg_color=("#DEDEDE", "#2E2E2E"))
            self.os_thread_wait.grid(sticky=tkinter.W)
            threading.Thread(target=self.thread_os).start()
            self.os_txt.configure(text='Sistema Operacional (-)')
            self.os_expanded_check = 1

    def thread_cpu(self):
        cpufreq = psutil.cpu_freq()
        ci.CTkLabel(self.cpu_expanded, text='Total de Core(s): '+str(psutil.cpu_count(logical=True)), fg_color=("#DEDEDE", "#2E2E2E"), text_font=(settings.code_injection['style']['font'], 13)).grid(sticky=tkinter.W)
        ci.CTkLabel(self.cpu_expanded, text='Frequência Max: '+str(f"{cpufreq.max:.2f}Mhz"), fg_color=("#DEDEDE", "#2E2E2E"), text_font=(settings.code_injection['style']['font'], 13)).grid(sticky=tkinter.W)
        ci.CTkLabel(self.cpu_expanded, text='Frequência Atual: '+str(f"{cpufreq.current:.2f}Mhz"), fg_color=("#DEDEDE", "#2E2E2E"), text_font=(settings.code_injection['style']['font'], 13)).grid(sticky=tkinter.W)
        self.cpu_thread_wait.destroy() 

    def cpu_expanded(self):
        if self.cpu_expanded_check == 1:
            self.cpu_expanded.destroy()
            self.cpu_txt.configure(text='Processador (+)')
            self.cpu_expanded_check = 0
        else:
            self.cpu_expanded = ci.CTkFrame(self.frame, fg_color=("#DEDEDE", "#2E2E2E"), height=15)
            self.cpu_expanded.grid(row=7, column=0, sticky=tkinter.W, padx=90, pady=0)
            self.cpu_thread_wait = ci.CTkLabel(self.cpu_expanded, text="coletando informações...", text_font=(settings.code_injection['style']['font'], 13), fg_color=("#DEDEDE", "#2E2E2E"))
            self.cpu_thread_wait.grid(sticky=tkinter.W)
            threading.Thread(target=self.thread_cpu).start()
            self.cpu_txt.configure(text='Processador (-)')
            self.cpu_expanded_check = 1

    def thread_mobo(self):
        self.mobo_thread_wait.destroy()
        ci.CTkLabel(self.mobo_expanded, text='Frabicante: '+str(settings.regedit("HARDWARE\\DESCRIPTION\\System\\BIOS",'BIOSVendor')), text_font=(settings.code_injection['style']['font'], 13), fg_color=("#DEDEDE", "#2E2E2E")).grid(sticky=tkinter.W)
        ci.CTkLabel(self.mobo_expanded, text='Versão: '+str(settings.regedit("HARDWARE\\DESCRIPTION\\System\\BIOS",'BIOSVersion')), text_font=(settings.code_injection['style']['font'], 13), fg_color=("#DEDEDE", "#2E2E2E")).grid(sticky=tkinter.W)
        ci.CTkLabel(self.mobo_expanded, text='Data de Fabricação: '+str(settings.regedit("HARDWARE\\DESCRIPTION\\System\\BIOS",'BIOSReleaseDate')), text_font=(settings.code_injection['style']['font'], 13), fg_color=("#DEDEDE", "#2E2E2E")).grid(sticky=tkinter.W)

    def mobo_expanded(self):
        if self.mobo_expanded_check == 1:
            self.mobo_expanded.destroy()
            self.mobo_txt.configure(text='Placa mãe (+)')
            self.mobo_expanded_check = 0
        else:
            self.mobo_expanded = ci.CTkFrame(self.frame, fg_color=("#DEDEDE", "#2E2E2E"), height=15)
            self.mobo_expanded.grid(row=11, column=0, sticky=tkinter.W, padx=90, pady=0)
            self.mobo_thread_wait = ci.CTkLabel(self.mobo_expanded, text="coletando informações...", text_font=(settings.code_injection['style']['font'], 13), fg_color=("#DEDEDE", "#2E2E2E"))
            self.mobo_thread_wait.grid(sticky=tkinter.W)
            threading.Thread(target=self.thread_mobo).start()
            self.mobo_txt.configure(text='Placa mãe (-)')
            self.mobo_expanded_check = 1

    def thread_network(self):    
        self.network_thread_wait.destroy()
        result = subprocess.Popen('wmic nicconfig where "IPEnabled  = True" get ipaddress,MACAddress,IPSubnet,DNSHostName,Caption,DefaultIPGateway,DNSServerSearchOrder /format:table', shell=True, startupinfo=settings.startupinfo, creationflags=settings.disable_terminal, stdout=subprocess.PIPE) 
        data = result.stdout.read().decode('utf-8')
        data = data.replace('\r', '').strip().split('\n')
        del data[0]
        for i in data:
            network = i.split('  ')
            for i in range(len(network)):
                try:
                    network.remove('')
                except Exception:
                    pass    
            try:  
                name = network[0]
                gateway = network[1].replace('"','').replace('{','').replace('}','')
                ip = network[4].replace('"','').replace('{','').replace('}','')
                mask = network[5].replace('"','').replace('{','').replace('}','')
                mac = network[6]
                dns = network[3].replace('"','').replace('{','').replace('}','')
                name = sub("([\(\[]).*?([\)\]])", "", name).lstrip()
            except:
                pass
            x = ci.CTkLabel(self.network_expanded, text=f'{name}', text_font=(settings.code_injection['style']['font'], 13), fg_color=("#DEDEDE", "#2E2E2E"))
            x.grid(sticky=tkinter.W, padx=15, pady=0)
            ci.CTkLabel(self.network_expanded, text=f'IP: {ip}', text_font=(settings.code_injection['style']['font'], 13), fg_color=("#DEDEDE", "#2E2E2E")).grid(sticky=tkinter.W, padx=40, pady=0)  
            ci.CTkLabel(self.network_expanded, text=f'Máscara: {mask}', text_font=(settings.code_injection['style']['font'], 13), fg_color=("#DEDEDE", "#2E2E2E")).grid(sticky=tkinter.W, padx=40, pady=0)  
            ci.CTkLabel(self.network_expanded, text=f'DNS: {dns}', text_font=(settings.code_injection['style']['font'], 13), fg_color=("#DEDEDE", "#2E2E2E")).grid(sticky=tkinter.W, padx=40, pady=0)  
            ci.CTkLabel(self.network_expanded, text=f'Gateway: {gateway}', text_font=(settings.code_injection['style']['font'], 13), fg_color=("#DEDEDE", "#2E2E2E")).grid(sticky=tkinter.W, padx=40, pady=0)

    def network_expanded(self):
        if self.network_expanded_check == 1:
            self.network_expanded.destroy()
            self.network_txt.configure(text='Rede (+)')
            self.network_expanded_check = 0
        else:
            self.network_expanded = ci.CTkFrame(self.frame, fg_color=("#DEDEDE", "#2E2E2E"), height=15)
            self.network_expanded.grid(row=34, column=0, sticky=tkinter.W, padx=90, pady=0)
            self.network_thread_wait = ci.CTkLabel(self.network_expanded, text="coletando informações...", text_font=(settings.code_injection['style']['font'], 13), fg_color=("#DEDEDE", "#2E2E2E"))
            self.network_thread_wait.grid(sticky=tkinter.W)
            threading.Thread(target=self.thread_network).start()
            self.network_txt.configure(text='Rede (-)')
            self.network_expanded_check = 1

    def onFrameConfigure(self,canvas):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def create_content(self):

        self.frame_content = ci.CTkFrame(self.master, corner_radius=0)
        self.frame_content.pack()
       

        '''
        self.frame = ci.CTkFrame(self.frame_content, corner_radius=0,height=70).pack()
        self.page = ci.CTkLabel(self.frame_content, text="SYSINFO", text_font=("Roboto Medium", 20))
        self.page.place(relx=0.4, rely=0.035)
        self.subpage = ci.CTkLabel(self.frame_content, text="Informações do OS e Hardware", text_font=(settings.code_injection['style']['font'], 12))
        self.subpage.place(relx=0.31, rely=0.085)
        '''
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


        self.frame = ci.CTkFrame(self.canvas, corner_radius=0)

        osimg = ImageTk.PhotoImage(Image.open(settings.folder_assets+"/img/icons/sysinfo/os.png"))
        self.os_txt = ci.CTkButton(self.frame, image=osimg, text='Sistema Operacional (+)', text_color=settings.hover_color, cursor="hand2", hover_color=None, text_font=(settings.code_injection['style']['font'], -17), border_width=0, fg_color=("#DEDEDE", "#2E2E2E"), command=self.os_expanded)
        self.os_txt.grid(row=1, column=0, sticky=tkinter.W, padx=25, pady=0)
        self.os = ci.CTkLabel(self.frame, text=settings.system+', '+settings.version, text_font=(settings.code_injection['style']['font'], 13), fg_color=("#DEDEDE", "#2E2E2E"))
        self.os.grid(row=2, column=0, sticky=tkinter.W, padx=90, pady=0)

        ci.CTkFrame(self.frame,height=15, border_width=0, fg_color=("#DEDEDE", "#2E2E2E")).grid(row=4, column=0, pady=0)

        cpuimg = ImageTk.PhotoImage(Image.open(settings.folder_assets+"/img/icons/sysinfo/processador.png"))
        self.cpu_txt = ci.CTkButton(self.frame, image=cpuimg, text='Processador (+)', text_color=settings.hover_color, cursor="hand2", hover_color=None, text_font=(settings.code_injection['style']['font'], -17), border_width=0, fg_color=("#DEDEDE", "#2E2E2E"), command=self.cpu_expanded)
        self.cpu_txt.grid(row=5, column=0, sticky=tkinter.W, padx=25, pady=0)
        self.cpu_result = ci.CTkLabel(self.frame,  text='coletando informação...', text_font=(settings.code_injection['style']['font'], 13), fg_color=("#DEDEDE", "#2E2E2E"))
        self.cpu_result.grid(row=6, column=0, sticky=tkinter.W, padx=25, pady=0)
        self.cpu_usage = ci.CTkLabel(self.frame,  text='--%', text_font=(settings.code_injection['style']['font'], 12), borderwidth=0, cursor="hand2", hover_color=None, text_color=("#DEDEDE", "#2E2E2E"))
        self.cpu_usage.grid(row=5, column=0, sticky=tkinter.W, padx=520, pady=0)

        ci.CTkFrame(self.frame, height=15, border_width=0, fg_color=("#DEDEDE", "#2E2E2E")).grid(row=8, column=0, pady=0)
        
        moboimg = ImageTk.PhotoImage(Image.open(settings.folder_assets+"/img/icons/sysinfo/mobo.png"))
        self.mobo_txt = ci.CTkButton(self.frame, image=moboimg, text='Placa mãe (+)', text_color=settings.hover_color, cursor="hand2", hover_color=None, text_font=(settings.code_injection['style']['font'], -17), border_width=0, fg_color=("#DEDEDE", "#2E2E2E"), command=self.mobo_expanded)
        self.mobo_txt.grid(row=9, column=0, sticky=tkinter.W, padx=25, pady=0)
        self.mobo_result = ci.CTkLabel(self.frame, text='coletando informação...', text_font=(settings.code_injection['style']['font'], 13), hover_color=None, fg_color=("#DEDEDE", "#2E2E2E"))
        self.mobo_result.grid(row=10, column=0, sticky=tkinter.W, padx=25, pady=0)

        ci.CTkFrame(self.frame, height=19, border_width=0, fg_color=("#DEDEDE", "#2E2E2E")).grid(row=12, column=0, pady=0)

        ramimg = ImageTk.PhotoImage(Image.open(settings.folder_assets+"/img/icons/sysinfo/ram.png"))
        self.ram_txt = ci.CTkButton(self.frame, image=ramimg, text='Memória RAM', text_color=settings.hover_color, cursor="hand2", hover_color=None, text_font=(settings.code_injection['style']['font'], -17), border_width=0, fg_color=("#DEDEDE", "#2E2E2E"))
        self.ram_txt.grid(row=13, column=0, sticky=tkinter.W, padx=25, pady=0)
        self.ram_result_main = ci.CTkLabel(self.frame, text='coletando informação...', text_font=(settings.code_injection['style']['font'], 13), hover_color=None, fg_color=("#DEDEDE", "#2E2E2E"))
        self.ram_result_main.grid(row=14, column=0, sticky=tkinter.W, padx=90, pady=0)
        self.ram_usage = ci.CTkButton(self.frame,  text='--%', text_font=(settings.code_injection['style']['font'], 12), borderwidth=0, cursor="hand2", hover_color=None, fg_color=("#DEDEDE", "#2E2E2E"))
        self.ram_usage.grid(row=13, column=0, sticky=tkinter.W, padx=520, pady=0)

        ci.CTkFrame(self.frame, height=15, border_width=0, fg_color=("#DEDEDE", "#2E2E2E")).grid(row=15, column=0, pady=0)

        gpuimg = ImageTk.PhotoImage(Image.open(settings.folder_assets+"/img/icons/sysinfo/gpu.png"))
        self.gpu_txt = ci.CTkButton(self.frame, image=gpuimg, text='Placa de Vídeo', text_color=settings.hover_color, cursor="hand2", hover_color=None, text_font=(settings.code_injection['style']['font'], -17), border_width=0, fg_color=("#DEDEDE", "#2E2E2E"))
        self.gpu_txt.grid(row=16, column=0, sticky=tkinter.W, padx=25, pady=0)
        self.gpu_result = ci.CTkLabel(self.frame, text='coletando informação...', text_font=(settings.code_injection['style']['font'], 13), fg_color=("#DEDEDE", "#2E2E2E"))
        self.gpu_result.grid(row=17, column=0, sticky=tkinter.W, padx=60, pady=0)

        ci.CTkFrame(self.frame, height=15, border_width=0, fg_color=("#DEDEDE", "#2E2E2E")).grid(row=19, column=0, pady=0)

        storageimg = ImageTk.PhotoImage(Image.open(settings.folder_assets+"/img/icons/sysinfo/storage.png"))
        self.storage_txt = ci.CTkButton(self.frame, image=storageimg, text='Armazenamento', text_color=settings.hover_color, cursor="hand2", hover_color=None, text_font=(settings.code_injection['style']['font'], -17), border_width=0, fg_color=("#DEDEDE", "#2E2E2E"))
        self.storage_txt.grid(row=20, column=0, sticky=tkinter.W, padx=25, pady=0)
        self.storage_result_main = ci.CTkLabel(self.frame, text='coletando informação...', text_font=(settings.code_injection['style']['font'], 13), fg_color=("#DEDEDE", "#2E2E2E"))
        self.storage_result_main.grid(row=21, column=0, sticky=tkinter.W, padx=90, pady=0)

        ci.CTkFrame(self.frame, height=20, border_width=0, fg_color=("#DEDEDE", "#2E2E2E")).grid(row=22, column=0, pady=0)

        monitorimg = ImageTk.PhotoImage(Image.open(settings.folder_assets+"/img/icons/sysinfo/monitor.png"))
        self.monitor_txt = ci.CTkButton(self.frame, image=monitorimg, text='Monitor', text_color=settings.hover_color, cursor="hand2", hover_color=None, text_font=(settings.code_injection['style']['font'], -17), border_width=0, fg_color=("#DEDEDE", "#2E2E2E"))
        self.monitor_txt.grid(row=23, column=0, sticky=tkinter.W, padx=25, pady=0)
        self.monitor_result = ci.CTkLabel(self.frame, text='coletando informação...', text_font=(settings.code_injection['style']['font'], 13), fg_color=("#DEDEDE", "#2E2E2E"))
        self.monitor_result.grid(row=24, column=0, sticky=tkinter.W, padx=90, pady=0)

        ci.CTkFrame(self.frame, height=15, border_width=0, fg_color=("#DEDEDE", "#2E2E2E")).grid(row=26, column=0, pady=0)

        audioimg = ImageTk.PhotoImage(Image.open(settings.folder_assets+"/img/icons/sysinfo/audio.png"))
        self.audio_txt = ci.CTkButton(self.frame, image=audioimg, text='Audio', text_color=settings.hover_color, cursor="hand2", hover_color=None, text_font=(settings.code_injection['style']['font'], -17), border_width=0, fg_color=("#DEDEDE", "#2E2E2E"))
        self.audio_txt.grid(row=27, column=0, sticky=tkinter.W, padx=25, pady=0)
        self.audio_result = ci.CTkLabel(self.frame, text='coletando informação...', text_font=(settings.code_injection['style']['font'], 13), fg_color=("#DEDEDE", "#2E2E2E"))
        self.audio_result.grid(row=28, column=0, sticky=tkinter.W, padx=90, pady=0)

        ci.CTkFrame(self.frame, height=15, border_width=0, fg_color=("#DEDEDE", "#2E2E2E")).grid(row=29, column=0, pady=0)

        networkimg = ImageTk.PhotoImage(Image.open(settings.folder_assets+"/img/icons/sysinfo/network.png"))
        self.network_txt = ci.CTkButton(self.frame, image=networkimg, text='Rede (+)', text_color=settings.hover_color, cursor="hand2", hover_color=None, text_font=(settings.code_injection['style']['font'], -17), border_width=0, fg_color=("#DEDEDE", "#2E2E2E"), command=self.network_expanded)
        self.network_txt.grid(row=31, column=0, sticky=tkinter.W, padx=25, pady=0)
        self.network_result = ci.CTkLabel(self.frame, text='coletando informação...', text_font=(settings.code_injection['style']['font'], 13), fg_color=("#DEDEDE", "#2E2E2E"))
        self.network_result.grid(row=32, column=0, sticky=tkinter.W, padx=90, pady=0)

        ci.CTkFrame(self.frame, height=15, border_width=0, fg_color=("#DEDEDE", "#2E2E2E")).grid(row=34, column=0, pady=0)

        licenseimg = ImageTk.PhotoImage(Image.open(settings.folder_assets+"/img/icons/sysinfo/license.png"))
        self.license_txt = ci.CTkButton(self.frame, image=licenseimg, text='Licenças', text_color=settings.hover_color, cursor="hand2", hover_color=None, text_font=(settings.code_injection['style']['font'], -17), border_width=0, fg_color=("#DEDEDE", "#2E2E2E"))
        self.license_txt.grid(row=36, column=0, sticky=tkinter.W, padx=25, pady=0)
        self.license_result = ci.CTkLabel(self.frame, text='coletando informação...', text_font=(settings.code_injection['style']['font'], 13), fg_color=("#DEDEDE", "#2E2E2E"))
        self.license_result.grid(row=37, column=0, sticky=tkinter.W, padx=90, pady=0)

        ci.CTkFrame(self.frame, height=15, border_width=0, fg_color=("#DEDEDE", "#2E2E2E")).grid(row=38, column=0, pady=0)  

        self.frame.bind("<Configure>", lambda event, canvas=self.canvas: self.onFrameConfigure(self.canvas))
        self.canvas.create_window(0, 0, anchor='nw', window=self.frame)
        self.canvas.update_idletasks()
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        self.canvas.configure(scrollregion=self.canvas.bbox('all'),yscrollcommand=scroll_y.set)                         
        self.canvas.pack(expand=True, side='left', pady=20)
        scroll_y.pack(fill='y', side='right',pady=20)

        try:
            threading.Thread(target=self.dashboard).start()
            threading.Thread(target=self.update_loop).start()
            threading.Thread(target=self.update_check).start()
        except:
            pass
