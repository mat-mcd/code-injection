from cpu_load_generator import load_single_core, load_all_cores, from_profile
import tkinter, threading, subprocess, socket, os
import customtkinter as ci
from tkinter import ttk, filedialog, messagebox, PhotoImage
from PIL import ImageTk, Image
from app import settings
from app import data
from app import logs
import sounddevice as sd
import numpy as np
import psutil
import time
import tkinter as tk
from pythonping import ping

class tools(ci.CTkFrame):
    def __init__(self, master):
        self.master = master
        self.user_data = data.UserData.get_instance()
        style = ttk.Style()
        style.theme_use("clam")
        self.MEGABYTE = 1024 * 1024
        self.create_content()
        self.__stress_finished = 0
        self.__stress_teste_num = 0

    def under_development(self,func):
        messagebox.showinfo('Aviso do Sistema', f'O teste "{func}" ainda não está disponível, aguarde as próximas atualizações!')

    def __test_port(self):
        test = ci.CTkInputDialog(master=self.master, text="Digite a IP:PORTA que deseja testar\nExemplo: 192.168.1.1:9999", title="Testar Porta")
        
        ip_port = test.get_input()
        try:
            ip = ip_port.split(":")[0]
            port = ip_port.split(":")[1]
        except Exception as e:
            messagebox.showinfo('Aviso do Sistema', f'Informe o ip:porta válido\nExemplo: 192.168.1.1:9999')

        if not test == '':
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                result = sock.connect_ex((f'{ip}',int(port)))
                if result == 0:
                    messagebox.showinfo('Aviso do Sistema', f'Verificação finalizada!\nA porta {port} está aberta')
                else:
                   messagebox.showinfo('Aviso do Sistema', f'Ooops!\nA porta {port} está fechada\n\nAtenção: Se você já liberou a porta e ainda consta como fechada, lembre-se, para a porta constar como aberta algum serviço deve esta rodando na mesma')
                sock.close()
            except Exception as e:
                messagebox.showinfo('Aviso do Sistema', f'Ocorreu um erro\n\n{e}')
        else:
            messagebox.showinfo('Aviso do Sistema', f'Informe a porta & ip que deseja checar')

    def test_port(self):
        threading.Thread(target=self.__test_port).start()

    def call_test_keyboard(self):
        threading.Thread(target=self.keyboard_test).start()

    def my_ip(self):  
        self.modal_ip = ci.CTkToplevel(self.master)
        self.modal_ip.title(f'Meu IP - {settings.app_name} v{settings.app_version}')
        self.modal_ip.geometry("580x380")
        self.modal_ip.iconbitmap(settings.folder_assets+'/img/code-injection.ico')

        self.frame_x = ci.CTkFrame(self.modal_ip, fg_color=("#DEDEDE", "#1F1F1F"), width=580)
        self.frame_x.grid(row=0, column=0, sticky=tkinter.W, padx=15, pady=15)
        from requests import get
        ip = get('https://api.ipify.org').text
        ci.CTkLabel(self.frame_x, text=f'Endereço de IP público (externo)'+' '*100, text_font=(settings.code_injection['style']['font'], 13)).grid(sticky=tkinter.W, padx=40, pady=0)  
        ci.CTkLabel(self.frame_x, text=f'{ip}\n', text_color='#32bea6', text_font=(settings.code_injection['style']['font'], 13)).grid(sticky=tkinter.W, padx=40, pady=0)  

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
                ip = network[4].replace('"','').replace('{','').replace('}','').split(',')
                name = sub("([\(\[]).*?([\)\]])", "", name).lstrip()
            except:
                pass

            ci.CTkLabel(self.frame_x, text=f'{name}', text_font=(settings.code_injection['style']['font'], 13)).grid(sticky=tkinter.W, padx=15, pady=0)
            ci.CTkLabel(self.frame_x, text=f'{ip[0]}\n', text_color='#32bea6', text_font=(settings.code_injection['style']['font'], 13)).grid(sticky=tkinter.W, padx=40, pady=0)  

    def __record_audio(self):
        fs=44100
        duration = 10
        myrecording = sd.rec(duration * fs, samplerate=fs, channels=2,dtype='float64')
        sd.wait()
        self.txt_mic.configure(text='Reproduzindo sua gravação...', text_color='#32bea6')
        sd.play(myrecording, fs)
        sd.wait()
        self.call_mic_teste.configure(text='Refazer Teste', state='enabled')
        self.txt_mic.configure(text='Teste finalizado!')
        messagebox.showinfo('Aviso do Sistema', 'Teste finalizado!\n\nSe você ouviu sua própria gravação o microfone está funcionando corretamente', parent=self.modal_mic)
        self.mic_test_is_running = False

    def __view_return(self):
        duration = 10
        def norm(indata, outdata, frames, time, status):
            volume_norm = np.linalg.norm(indata)*10
            try:
                if volume_norm >= 80:
                    x = "|" * int(volume_norm)
                    self.mic_level.configure(text=x[:80], text_color="red")
                elif volume_norm >= 40:
                    self.mic_level.configure(text="|" * int(volume_norm), text_color="yellow")
                elif volume_norm <= 35:
                    self.mic_level.configure(text="|" * int(volume_norm), text_color="green")
            except:
                pass
        with sd.Stream(channels=2, callback=norm):
            sd.sleep(int(5000 * 1000))

    def check_update(self):
        if settings.check_network():
            self.network_status['text'] = 'Conexão com a Internet: OK'
            import requests, sys, os
            from tkinter.messagebox import askyesno
            try:
                r = requests.post(settings.url_check_update)
                result = r.json()
          
                if Settings.code_injection['app_version'] < result['version']:

                    answer = askyesno(title='Nova atualização encontrada', message='Uma nova versão está disponível para download\nVersão Atual: '+Settings.code_injection['app_version']+'\nNova versão: '+result['version']+'\n\nDesejar atualizar?')
                    if answer:
                        subprocess.Popen([Settings.folder_assets+'/update.exe', Settings.folder_assets], creationflags=Settings.CREATE_NO_WINDOW)
                        sys.exit(1)    
            except Exception as e:
                messagebox.showinfo("Aviso do Sistema", 'Ocorreu um erro\n\n'+str(e))
        else:
            self.network_status['text'] = 'Conexão com a Internet: Desconectado'         

    def call_mic_teste(self, event=None):
        if self.mic_test_is_running == True:
            pass
        else:
            self.mic_test_is_running = True
            self.call_mic_teste.configure(text='Gravando...', state='disabled')
            self.txt_mic.configure(text='Diga "Olá" ou faça algum barulho, estamos gravando...')
            threading.Thread(target=self.__record_audio).start()  

    def test_mic(self):
        self.modal_mic = ci.CTkToplevel(self.master)
        self.modal_mic.title(f'Teste de Microfone - {settings.app_name} v{settings.app_version}')
        self.modal_mic.geometry("450x220")
        self.modal_mic.iconbitmap(settings.folder_assets+'/img/code-injection.ico')
        self.modal_mic.bind('<Return>', self.call_mic_teste)
        self.mic_test_is_running = False

        self.frame = ci.CTkLabel(self.modal_mic, text='').pack()

        self.txt = ci.CTkLabel(self.modal_mic, text='Teste de Microfone', text_font=(settings.code_injection['style']['font'], 20))
        self.txt.pack()

        self.txt_mic = ci.CTkLabel(self.modal_mic, text='Clique no botão abaixo para iniciar o teste', text_font=(settings.code_injection['style']['font'], 10))
        self.txt_mic.pack()

        threading.Thread(target=self.__view_return).start()

        self.mic_level = ci.CTkLabel(self.modal_mic, text="")
        self.mic_level.pack(pady=10)

        self.call_mic_teste = ci.CTkButton(self.modal_mic, text='Iniciar Teste', text_font=(settings.code_injection['style']['font'], 11), command=self.call_mic_teste)
        self.call_mic_teste.pack(pady=20)

    def start_webcam(self):
        settings.terminal(settings.folder_assets+'/scripts/webcam/Webcam.exe /P')

    def test_webcam(self):  
        t=threading.Thread(target=self.start_webcam)
        t.start()

    def call_test_network(self, event=None):
        if self.net_test_is_running == True:
            pass
        else:
            self.net_test_is_running = True
            threading.Thread(target=self.start_test_network).start()

    def call_my_ip(self):
        threading.Thread(target=self.my_ip).start()

    def start_test_network(self):
        self.botao_testar.configure(text='Verificando sua conexão, aguarde...')
        import speedtest
        speed = speedtest.Speedtest()
        speed.get_best_server()        

        download = f"{'{:.2f}'.format(speed.download()/1024/1024)}"
        self.l_download.configure(text=download)
        self.l_download.place(x=20, y=25)
        
        upload = f"{'{:.2f}'.format(speed.upload()/1024/1024)} "
        self.l_upload.configure(text=upload)
        self.l_upload.place(x=235, y=25)
        
        self.botao_testar.configure(text='Testar novamente')
        self.ping_result.configure(text= f'{speed.results.ping} ms')
        self.net_test_is_running = False

    def test_network(self):
            self.modal = ci.CTkToplevel(self.master)
            self.modal.title(f'Teste de Conexão - {settings.app_name} v{settings.app_version}')
            self.modal.geometry('350x235')
            self.modal.resizable(0,0)
            self.modal.iconbitmap(settings.folder_assets+'/img/code-injection.ico')
            self.modal.bind('<Return>', self.call_test_network)
            self.net_test_is_running = False

            frame_logo = ci.CTkFrame(self.modal,width=400, height=60, corner_radius=0)
            frame_logo.grid(row=0, column=0,pady=1, padx=0, sticky=tkinter.NSEW)

            frame_corpo = ci.CTkFrame(self.modal,width=400, height=200, corner_radius=0)
            frame_corpo.grid(row=1, column=0,pady=1, padx=0, sticky=tkinter.NSEW)

            img = Image.open(settings.folder_assets+'/img/icons/tools/teste-internet.png')
            img = img.resize((55, 55), Image.ANTIALIAS)
            img = ImageTk.PhotoImage(img)

            app_imagem = ci.CTkLabel(frame_logo, text='', height=60, image=img, compound=tkinter.LEFT,padx=10, anchor="nw", text_font=('Ivy 16 bold'), bg="#feffff", fg="#fc766d")
            app_imagem.image = img
            app_imagem.place(x=0, y=0)

            l_nome = ci.CTkLabel(frame_logo, text="Teste de Conexão", height=1,anchor=tkinter.NE, text_font=(settings.code_injection['style']['font'], 18), bg="#feffff", fg="#403d3d")
            l_nome.place(x=90, y=10)

            l_linha = ci.CTkLabel(frame_logo, width=445, text="", height=1,anchor=tkinter.NW, text_font=('Ivy 1 '))
            l_linha.place(x=0, y=57)

            img_down = Image.open(settings.folder_assets+'/img/icons/tools/down.png')
            img_down = img_down.resize((50, 50), Image.ANTIALIAS)
            img_down = ImageTk.PhotoImage(img_down)
            app_imagem = ci.CTkLabel(frame_corpo, text='', width=40, height=60, image=img_down, compound=tkinter.LEFT, padx=10, relief="flat", anchor="nw", text_font=('Ivy 16 bold'))
            app_imagem.image = img_down
            app_imagem.place(x=125, y=20)

            l_mbps = ci.CTkLabel(frame_corpo, text="Download", anchor=tkinter.NW, text_font=(settings.code_injection['style']['font'], 10))
            l_mbps.place(x=5, y=5)
            self.l_download = ci.CTkLabel(frame_corpo, text="--", height=1, anchor=tkinter.NW, text_font=('arial 28'))
            self.l_download.place(x=0, y=25)
            l_mbps = ci.CTkLabel(frame_corpo, text="Mbps", height=1, anchor=tkinter.NW, text_font=('Ivy 10'))
            l_mbps.place(x=0, y=70)


            img_up = Image.open(settings.folder_assets+'/img/icons/tools/up.png')
            img_up = img_up.resize((50, 50), Image.ANTIALIAS)
            img_up = ImageTk.PhotoImage(img_up)

            app_imagem = ci.CTkLabel(frame_corpo, text='', width=40, height=60, image=img_up, compound=tkinter.LEFT, padx=10, relief="flat", anchor="nw", text_font=('Ivy 16 bold'))
            app_imagem.image = img_up
            app_imagem.place(x=170, y=20)

            l_mbps = ci.CTkLabel(frame_corpo, text="Upload", anchor=tkinter.NW, text_font=(settings.code_injection['style']['font'], 10))
            l_mbps.place(x=230, y=5)
            self.l_upload = ci.CTkLabel(frame_corpo, text="--", anchor=tkinter.NW, text_font=('arial 28'))
            self.l_upload.place(x=230, y=25)
            l_mbps = ci.CTkLabel(frame_corpo, text="Mbps", anchor=tkinter.NW, text_font=(settings.code_injection['style']['font'], 10))
            l_mbps.place(x=230, y=70)

            ping = ci.CTkLabel(frame_corpo, text="Ping: ", anchor=tkinter.NW, text_font=(settings.code_injection['style']['font'], 10))
            ping.place(x=100, y=90)

            self.ping_result = ci.CTkLabel(frame_corpo, width=0, text="-- ms", anchor=tkinter.NW, text_font=(settings.code_injection['style']['font'], 10))
            self.ping_result.place(x=180, y=90)

            self.botao_testar = ci.CTkButton(frame_corpo, text="Iniciar teste", width=290, text_font=(settings.code_injection['style']['font'], 10), command=self.call_test_network)
            self.botao_testar.place(x=30, y=130)

    def __cpu_data(self, none=None):
        try:
            self.cpu_cores_text.configure(text=f"{int(self.cpu_cores.get())}")
            self.cpu_consumption_text.configure(text=f"{int(self.cpu_consumption.get())}%")
        except:
            pass

    def __ram_data(self, none=None):
        try:
            self.ram_consumption_text.configure(text=f"{int(self.ram_consumption.get())}MB")
        except:
            pass

    def __check_is_finished(self):
        if not self.__stress_teste_num < self.__stress_finished:
            self.start_button.configure(state='enabled')
            self.stress_test_is_running = False

    def __ram_test(self):
        self.__log(2, "INICIANDO TESTE NA MEMORIA RAM")
        memory = self.ram_consumption.get()
        self.__log(2, f"ALOCANDO {memory}MB")
        dummy_buffer = []
        self.__log(2, f"{memory}MB FORAM ALOCADOS")
        dummy_buffer = ['*' * self.MEGABYTE for _ in range(0, int(memory))]
        time.sleep(int(self.ram_time.get()))
        self.__log(2, f'TESTE FINALIZADO')
        threading.Thread(target=settings.notification("O Teste de Stress na Memória RAM foi finalizado", 15)).start()
        self.__stress_finished += 1
        self.__check_is_finished()

    def __cpu_test(self):
        self.__log(1, "INICIANDO TESTE NO PROCESSADOR !")
        cores = int(self.cpu_cores.get())
        consumption = int(self.cpu_consumption.get()) / 100
        time = int(self.cpu_time.get())
        if cores < psutil.cpu_count(logical=True):
            for i in range(cores):
                self.__log(1, f'NUCLEO {i} EM STRESS / {int(consumption * 100)}%')
                threading.Thread(target=load_single_core(core_num=i, duration_s=time, target_load=consumption)).start()
            self.__log(1, f'TESTE FINALIZADO')
            threading.Thread(target=settings.notification("O Teste de Stress no Processador foi finalizado", 15)).start()
            self.__stress_finished += 1
            self.__check_is_finished()
        else:
            self.__log(1, f'TODOS OS NUCLEOS EM STRESS / {int(consumption * 100)}%')
            threading.Thread(target=load_all_cores(duration_s=time, target_load=consumption)).start()
            self.__log(1, f'TESTE FINALIZADO')
            threading.Thread(target=settings.notification("O Teste de Stress no Processador foi finalizado", 15)).start()
            self.__stress_finished += 1
            self.__check_is_finished()

    def __start_stress(self, event=None):
        if self.stress_test_is_running == True:
            pass
        else:
            self.stress_test_is_running = True
            t = threading.Thread(target=self.__stress)
            t.start()

    def __stress(self):
        self.start_button.configure(state='disabled')
        self.logs_frame.destroy()
        self.logs_frame = ci.CTkFrame(self.logs_main_frame, fg_color=("gray80", "gray22"), height=0)
        self.logs_frame.pack(pady=3)
        if self.cpu_checkbox.get():
            self.__stress_teste_num += 1
            t = threading.Thread(target=self.__cpu_test)
            t.start()
        if self.ram_checkbox.get():
            self.__stress_teste_num += 1
            t = threading.Thread(target=self.__ram_test)
            t.start()

    def __update_dials(self):
        cpu = psutil.cpu_percent()
        self.cpu_percent.configure(text=f" {int(cpu)}%")
        self.cpu_percent_bar.set(int(cpu) / 100)

        memory = psutil.virtual_memory()[2]
        self.ram_percent.configure(text=f" {int(memory)}%")
        self.ram_percent_bar.set(int(memory) / 100)

        self.master.after(1000, self.__update_dials)

    def __log(self, type, text):
        if type == 1:
            img = Image.open(settings.folder_assets+"/img/icons/sysinfo/processador.png")
        elif type == 2:
            img = Image.open(settings.folder_assets+"/img/icons/sysinfo/ram.png")
        img = img.resize((20,20),Image.ANTIALIAS)
        img = ImageTk.PhotoImage(img)
        frame = ci.CTkFrame(self.logs_frame, fg_color=("gray80", "gray22"))
        frame.pack(fill="both")
        log_image = ci.CTkLabel(frame, text="", image=img, width=0, fg_color=("gray80", "gray22"))
        log_image.pack(side="left")
        log_image.image = img
        ci.CTkLabel(frame, text=text, width=0, fg_color=("gray80", "gray22")).pack(side="left", padx=10)

    def call_stress(self):
        t = threading.Thread(target=self.stress_test)
        t.start()

    def stress_test(self):
        self.modal = ci.CTkToplevel(self.master)
        self.modal.title(f'Teste de Stress - {settings.app_name} v{settings.app_version}')
        self.modal.geometry('600x320')
        self.modal.resizable(0,0)
        self.modal.iconbitmap(settings.folder_assets+'/img/code-injection.ico')
        self.modal.bind('<Return>', self.__start_stress)
        self.stress_test_is_running = False

        self.left_frame = ci.CTkFrame(self.modal, width=270, height=320)
        self.left_frame.propagate(0)
        self.left_frame.grid(row=0, column=0, sticky="nswe")

        self.right_frame = ci.CTkFrame(self.modal, width=350, height=320)
        self.right_frame.propagate(0)
        self.right_frame.grid(row=0, column=1, sticky="nswe")

        self.frame = ci.CTkFrame(self.left_frame, width=0, height=0)
        self.frame.pack(fill="both", pady=5)

        self.frame = ci.CTkFrame(self.left_frame)
        self.frame.pack(fill="both", pady=10)

        self.cpuimg = ImageTk.PhotoImage(Image.open(settings.folder_assets+"/img/icons/sysinfo/processador.png"))
        self.cpu = ci.CTkButton(self.frame, image=self.cpuimg, text='Processadorﾠﾠ', text_color=settings.hover_color, cursor="hand2", hover_color=None, text_font=(settings.code_injection['style']['font'], -17), border_width=0, fg_color=("#DEDEDE", "#2E2E2E"))
        self.cpu.pack(side="left", padx=10)
        self.cpu.image = self.cpuimg

        self.cpu_checkbox = ci.CTkCheckBox(self.frame, text="")
        self.cpu_checkbox.pack(side="left", padx=10)

        self.frame = ci.CTkFrame(self.left_frame)
        self.frame.pack(fill="both", pady=0)

        ci.CTkLabel(self.frame, text="ﾠﾠNucleos:ﾠ", width=0).pack(side="left", padx=5)

        self.cpu_cores = ci.CTkSlider(self.frame, width=100, from_=0, to=psutil.cpu_count(logical=True), number_of_steps=psutil.cpu_count(logical=True), command=self.__cpu_data)
        self.cpu_cores.pack(side="left")
        self.cpu_cores.set(0)

        self.cpu_cores_text = ci.CTkLabel(self.frame, text="0", width=0)
        self.cpu_cores_text.pack(side="left")

        self.frame = ci.CTkFrame(self.left_frame)
        self.frame.pack(fill="both", pady=0)

        ci.CTkLabel(self.frame, text="ﾠﾠConsumo:", width=0).pack(side="left", padx=5)

        self.cpu_consumption = ci.CTkSlider(self.frame, width=100, from_=0, to=100, number_of_steps=100, command=self.__cpu_data)
        self.cpu_consumption.pack(side="left")
        self.cpu_consumption.set(0)

        self.cpu_consumption_text = ci.CTkLabel(self.frame, text="0%", width=0)
        self.cpu_consumption_text.pack(side="left")

        self.frame = ci.CTkFrame(self.left_frame)
        self.frame.pack(fill="both", pady=0)

        ci.CTkLabel(self.frame, text="ﾠﾠTempo:ﾠﾠ", width=0).pack(side="left", padx=5)

        self.cpu_time = ci.CTkEntry(self.frame, width=50, height=20)
        self.cpu_time.pack(side="left")

        ci.CTkLabel(self.frame, text="s", width=0).pack(side="left")

        self.frame = ci.CTkFrame(self.left_frame, height=0, width=0)
        self.frame.pack(fill="both", pady=10)

        self.frame = ci.CTkFrame(self.left_frame)
        self.frame.pack(fill="both", pady=0)

        self.ramimg = ImageTk.PhotoImage(Image.open(settings.folder_assets+"/img/icons/sysinfo/ram.png"))
        self.ram = ci.CTkButton(self.frame, image=self.cpuimg, text='Memoria RAM', text_color=settings.hover_color, cursor="hand2", hover_color=None, text_font=(settings.code_injection['style']['font'], -17), border_width=0, fg_color=("#DEDEDE", "#2E2E2E"))
        self.ram.pack(side="left", padx=10)
        self.ram.image =self.ramimg

        self.ram_checkbox = ci.CTkCheckBox(self.frame, text="")
        self.ram_checkbox.pack(side="left", padx=10)

        self.frame = ci.CTkFrame(self.left_frame)
        self.frame.pack(fill="both", pady=0)

        ci.CTkLabel(self.frame, text="ﾠﾠConsumo:", width=0).pack(side="left", padx=5)

        self.ram_consumption = ci.CTkSlider(self.frame, width=100, from_=0, to=int(psutil.virtual_memory()[0] / self.MEGABYTE), number_of_steps=int(psutil.virtual_memory()[0] / self.MEGABYTE), command=self.__ram_data)
        self.ram_consumption.pack(side="left")
        self.ram_consumption.set(0)

        self.ram_consumption_text = ci.CTkLabel(self.frame, text="0MB", width=0)
        self.ram_consumption_text.pack(side="left", padx=5)

        self.frame = ci.CTkFrame(self.left_frame)
        self.frame.pack(fill="both", pady=0)

        ci.CTkLabel(self.frame, text="ﾠﾠTempo:ﾠﾠ", width=0).pack(side="left", padx=5)

        self.ram_time = ci.CTkEntry(self.frame, width=50, height=20)
        self.ram_time.pack(side="left")

        ci.CTkLabel(self.frame, text="s", width=0).pack(side="left")

        self.frame = ci.CTkFrame(self.left_frame)
        self.frame.pack(fill="both", pady=0)

        self.start_button = ci.CTkButton(self.frame, text="Iniciar", command=self.__start_stress)
        self.start_button.pack(side="bottom", pady=25)

        self.frame = ci.CTkFrame(self.right_frame, height=0)
        self.frame.pack(fill="both", pady=10)

        self.logs_main_frame = ci.CTkFrame(self.frame, width=310, height=250, fg_color=("gray80", "gray22"))
        self.logs_main_frame.propagate(0)
        self.logs_main_frame.pack(side="left", padx=10)
        self.logs_frame = ci.CTkFrame(self.logs_main_frame, fg_color=("gray80", "gray22"), height=0)
        self.logs_frame.pack(pady=3)
        ci.CTkFrame(self.logs_frame, fg_color=("gray80", "gray22"), height=0).pack(pady=3)

        self.frame = ci.CTkFrame(self.right_frame, height=0)
        self.frame.pack(fill="both")

        ci.CTkLabel(self.frame, text="RAM:ﾠ", width=0).pack(side="left", padx=10)
        self.ram_percent_bar = ci.CTkProgressBar(self.frame, width=220)
        self.ram_percent_bar.pack(side="left")
        self.ram_percent = ci.CTkLabel(self.frame, text="0%", width=0)
        self.ram_percent.pack(side="left", padx=5)

        self.frame = ci.CTkFrame(self.right_frame, height=0)
        self.frame.pack(fill="both")

        ci.CTkLabel(self.frame, text="CPU:ﾠ", width=0).pack(side="left", padx=10)
        self.cpu_percent_bar = ci.CTkProgressBar(self.frame, width=220)
        self.cpu_percent_bar.pack(side="left")
        self.cpu_percent = ci.CTkLabel(self.frame, text="0%", width=0)
        self.cpu_percent.pack(side="left", padx=5)

        self.__update_dials()

    def __get_pressed_keys(self, event=None):
        key = event.keysym
        ci.CTkLabel(self.keys_pressed, text=key.upper(), fg_color=("#DEDEDE",'gray22'), height=50, width=50).pack(side="right", padx=5)

    def keyboard_test(self):
        self.modal = ci.CTkToplevel(self.master)
        self.modal.title(f'Teste de teclado - {settings.app_name} v{settings.app_version}')
        self.modal.geometry('500x180')
        self.modal.resizable(0,0)
        self.modal.iconbitmap(settings.folder_assets+'/img/code-injection.ico')

        self.txt = ci.CTkLabel(self.modal, text='Teste de Teclado', text_font=(settings.code_injection['style']['font'], 20))
        self.txt.pack()

        self.txt_mic = ci.CTkLabel(self.modal, text='Monitorando em tempo real todas as teclas pressionadas', text_font=(settings.code_injection['style']['font'], 10))
        self.txt_mic.pack()

        self.frame = ci.CTkFrame(self.modal, height=50, fg_color=("#f2f2f2", "#1f1f1f"))
        self.frame.pack(padx=20, pady=20, fill="both")

        self.keys_pressed = ci.CTkFrame(self.frame, height=0, fg_color=("#f2f2f2", "#1f1f1f"))
        self.keys_pressed.place(x=0, y=0)

        self.modal.bind("<Key>", self.__get_pressed_keys)

    def __quit_screen_test(self, event=None):
        self.modal.destroy()

    def __screen_test(self):
        if self.__screen_test_color == len(self.colors):
            self.__screen_test_color = 0
        self.modal.configure(background=self.colors[self.__screen_test_color])
        self.__screen_test_color += 1
        self.modal.after(500, self.__screen_test)

    def screen_test(self):
        self.modal = tk.Tk()
        self.modal.title(f'Teste de tela - {settings.app_name} v{settings.app_version}')
        self.modal.geometry('100x100')
        self.modal.attributes('-fullscreen', True)
        self.modal.focus_force()
        self.modal.resizable(0,0)
        self.modal.iconbitmap(settings.folder_assets+'/img/code-injection.ico')
        self.colors = ['red', 'blue', 'green']
        self.__screen_test_color = 0

        self.modal.bind("<Escape>", self.__quit_screen_test)
        self.modal.configure(background="red")
        self.modal.after(500, self.__screen_test)

        ci.CTkLabel(self.modal, text="APERTE ESC PARA SAIR", text_font=(settings.code_injection['style']['font'], 30)).pack(pady=20,anchor=tk.CENTER)

    def __ping_teste(self):
        if self.ping_test_is_running == True:
            pass
        else:
            self.ping_test_is_running = True
            ip = self.ip.get()
            packages = self.packages.get()
            interval = self.interval.get()
            min = 100000
            max = 0
            avg = 0
            package = 0
            while True:
                send = str(ping(f"{ip}", count=1)).replace('\n', '').split('\r')
                send.remove('')
                response = send[0].replace('Reply from', 'Resposta de').replace('in', 'em')
                min_avg_max = send[1].replace('Round Trip Times min/avg/max is ', '').replace(' ms', '').split('/')
                if float(min_avg_max[0]) < min:
                    min = float(min_avg_max[0])
                if float(min_avg_max[2]) > max:
                    max = float(min_avg_max[2])
                avg = float(min_avg_max[1])
                self.min_avg_max.configure(text=f"MIN:{min}ms     AVG:{avg}ms     MAX:{max}ms")
                self.listbox.insert(0, response+f", pacote: {package}")
                package += 1
                time.sleep(float(interval))
                if package > int(packages):
                    self.ping_test_is_running = False
                    break

    def call_ping_test(self, event=None):
        threading.Thread(target=self.__ping_teste).start()

    def ping_test(self):
        self.modal = ci.CTkToplevel(self.master)
        self.modal.title(f'Teste de Ping - {settings.app_name} v{settings.app_version}')
        self.modal.geometry('700x400')
        self.modal.resizable(0,0)
        self.modal.iconbitmap(settings.folder_assets+'/img/code-injection.ico')
        self.modal.bind('<Return>', self.call_ping_test)
        self.ping_test_is_running = False

        self.frame = ci.CTkFrame(self.modal)
        self.frame.pack(fill="both", pady=20, padx=20)

        self.frame_left = ci.CTkFrame(self.frame)
        self.frame_left.pack(fill="both", side="left")

        self.frame_right = ci.CTkFrame(self.frame)
        self.frame_right.pack(fill="both", side="right")

        self.frame = ci.CTkFrame(self.frame_left)
        self.frame.pack(fill="both")

        ci.CTkLabel(self.frame, text="", width=0, height=15, text_font=(settings.code_injection['style']['font'], -15)).pack(pady=5)

        ci.CTkLabel(self.frame, text="IP:", width=0, text_font=(settings.code_injection['style']['font'], -15)).pack(side="left", padx=20, pady=5)
        self.ip = ci.CTkEntry(self.frame, placeholder_text="192.168.1.1", width=120, height=25)
        self.ip.pack(side="left")

        self.frame = ci.CTkFrame(self.frame_left)
        self.frame.pack(fill="both")

        ci.CTkLabel(self.frame, text="Pacotes:", width=0, text_font=(settings.code_injection['style']['font'], -15)).pack(side="left", padx=20, pady=5)
        self.packages = ci.CTkEntry(self.frame, placeholder_text="5000", width=60, height=25)
        self.packages.pack(side="left")

        self.frame = ci.CTkFrame(self.frame_left)
        self.frame.pack(fill="both")

        ci.CTkLabel(self.frame, text="Intervalo:", width=0, text_font=(settings.code_injection['style']['font'], -15)).pack(side="left", padx=20, pady=5)
        self.interval = ci.CTkEntry(self.frame, width=50, placeholder_text="1", height=25)
        self.interval.pack(side="left")
        ci.CTkLabel(self.frame, text="s", width=0).pack(side="left")

        self.frame = ci.CTkFrame(self.frame_left)
        self.frame.pack(fill="both")

        self.start_button = ci.CTkButton(self.frame, text="INICIAR", command=lambda: threading.Thread(target=self.__ping_teste).start())
        self.start_button.pack(pady=20)

        self.frame = ci.CTkFrame(self.frame_right)
        self.frame.pack(side="left")

        if settings.code_injection['style']['theme'] == 'light':
            color = 'gray30'
        else:
            color = 'gray75'

        self.listbox = tkinter.Listbox(self.frame, bg=settings.font_color, selectbackground=settings.bg_color, fg=color, height=15, width=55, font=(settings.code_injection['style']['font'], 11), bd=0, highlightbackground=settings.bg_color, highlightthickness=3)
        self.listbox.pack()

        scrollbar = ttk.Scrollbar(self.frame_right)
        scrollbar.pack(side ='right', fill='both')
        self.listbox.config(yscrollcommand = scrollbar.set)

        scrollbar.config(command = self.listbox.yview)


        self.min_avg_max = ci.CTkLabel(self.frame, text="")
        self.min_avg_max.pack()

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1*(event.delta/110)), "units")

    def onFrameConfigure(self,canvas):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def create_content(self):
        self.middle_frame = ci.CTkFrame(self.master, height=550)
        self.middle_frame.propagate(0) 
        self.middle_frame.pack(padx=20, pady=20, fill='both')


        self.page = ci.CTkLabel(self.middle_frame, text="FERRAMENTAS", text_font=("Roboto Medium", 20))
        self.page.place(relx=0.33, rely=0.1)



        self.canvas = ci.CTkCanvas(self.middle_frame, background=settings.bg_color, bd=0, highlightthickness=0, relief='ridge')
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        self.frame = ci.CTkFrame(self.canvas, width=200, bd= 0)
        self.frame.pack(expand=False)

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

        vsb = ttk.Scrollbar(self.middle_frame, orient="vertical", command=self.canvas.yview, style="My.Vertical.TScrollbar")
        self.canvas.configure(yscrollcommand=vsb.set)
 
        #vsb.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        self.canvas.create_window((0,0), window=self.frame, anchor="nw")
    
        self.frame.bind("<Configure>", lambda event, canvas=self.canvas: self.onFrameConfigure(self.canvas))
        
        self.txt = ci.CTkLabel(self.frame, text='TESTES', text_font=("Roboto Medium", 20))
        self.txt.grid(row=0, column=0, pady=10)     

        ci.CTkFrame(self.frame,height=15).grid(row=1, column=0)
        self.item_frame = ci.CTkFrame(self.frame)
        self.item_frame.grid(padx=20)


        _img = PhotoImage(file=settings.folder_assets+"/img/icons/tools/teste-stress.png")
        self.img = ci.CTkButton(self.item_frame, image=_img, width=110, height=90, text="Stress", hover_color=("gray75", "gray30"), fg_color=("#e5e5e5", "#353535"), compound="top", text_font=(settings.code_injection['style']['font'], 12), command=self.call_stress)
        self.img.image = _img
        self.img.pack(side="left", padx=5)
     

        _img = PhotoImage(file=settings.folder_assets+"/img/icons/tools/webcam.png")
        self.img = ci.CTkButton(self.item_frame, image=_img, width=110, height=90, text="Webcam", hover_color=("gray75", "gray30"), fg_color=("#e5e5e5", "#353535"), compound="top", text_font=(settings.code_injection['style']['font'], 12), command=self.test_webcam)
        self.img.image = _img
        self.img.pack(side="left", padx=5)


        _img = PhotoImage(file=settings.folder_assets+"/img/icons/tools/mic.png")
        self.img = ci.CTkButton(self.item_frame, image=_img, width=110, height=90, text="Microfone", hover_color=("gray75", "gray30"), fg_color=("#e5e5e5", "#353535"), compound="top", text_font=(settings.code_injection['style']['font'], 12), command=self.test_mic)
        self.img.image = _img
        self.img.pack(side="left", padx=5)


        _img = PhotoImage(file=settings.folder_assets+"/img/icons/tools/teclado.png")
        self.img = ci.CTkButton(self.item_frame, image=_img, width=110, height=90, text="Teclado", hover_color=("gray75", "gray30"), fg_color=("#e5e5e5", "#353535"), compound="top", text_font=(settings.code_injection['style']['font'], 12), command=self.call_test_keyboard)
        self.img.image = _img
        self.img.pack(side="left", padx=5)


        _img = PhotoImage(file=settings.folder_assets+"/img/icons/tools/monitor.png")
        self.img = ci.CTkButton(self.item_frame, image=_img, width=110, height=90, text="Tela", hover_color=("gray75", "gray30"), fg_color=("#e5e5e5", "#353535"), compound="top", text_font=(settings.code_injection['style']['font'], 12), command=self.screen_test)
        self.img.image = _img
        self.img.pack(side="left", padx=5)



        ##############################################################################
        ci.CTkFrame(self.frame,height=15).grid(row=3, column=0)
        self.item_frame = ci.CTkFrame(self.frame)
        self.item_frame.grid(padx=20)


        _img = PhotoImage(file=settings.folder_assets+"/img/icons/tools/teste-internet.png")
        self.img = ci.CTkButton(self.item_frame, image=_img, width=110, height=90, text="Internet", hover_color=("gray75", "gray30"), fg_color=("#e5e5e5", "#353535"), compound="top", text_font=(settings.code_injection['style']['font'], 12), command=self.test_network)
        self.img.image = _img
        self.img.pack(side="left", padx=5)

        _img = PhotoImage(file=settings.folder_assets+"/img/icons/tools/porta.png")
        self.img = ci.CTkButton(self.item_frame, image=_img, width=110, height=90, text="Porta", hover_color=("gray75", "gray30"), fg_color=("#e5e5e5", "#353535"), compound="top", text_font=(settings.code_injection['style']['font'], 12), command=self.test_port)
        self.img.image = _img
        self.img.pack(side="left", padx=5)

        #blank
        ci.CTkButton(self.item_frame, width=110, height=90, text="", hover_color=("#DEDEDE", "#2E2E2E"), fg_color=("#DEDEDE", "#2E2E2E")).pack(side="left", padx=5)
        ci.CTkButton(self.item_frame, width=110, height=90, text="", hover_color=("#DEDEDE", "#2E2E2E"), fg_color=("#DEDEDE", "#2E2E2E")).pack(side="left", padx=5)
        ci.CTkButton(self.item_frame, width=110, height=90, text="", hover_color=("#DEDEDE", "#2E2E2E"), fg_color=("#DEDEDE", "#2E2E2E")).pack(side="left", padx=5)


        self.txt = ci.CTkLabel(self.frame, text='\nÚTILITARIOS', text_font=("Roboto Medium", 20))
        self.txt.grid(row=5, column=0, pady=20)  

        ci.CTkFrame(self.frame,height=15).grid(row=3, column=0)
        self.item_frame = ci.CTkFrame(self.frame)
        self.item_frame.grid(padx=20)


        _img = PhotoImage(file=settings.folder_assets+"/img/icons/tools/ip.png")
        self.img = ci.CTkButton(self.item_frame, image=_img, width=110, height=90, text="Meu IP", hover_color=("gray75", "gray30"), fg_color=("#e5e5e5", "#353535"), compound="top", text_font=(settings.code_injection['style']['font'], 12), command=self.call_my_ip)
        self.img.image = _img
        self.img.pack(side="left", padx=5)


        _img = PhotoImage(file=settings.folder_assets+"/img/icons/tools/ping.png")
        self.img = ci.CTkButton(self.item_frame, image=_img, width=110, height=90, text="Ping", hover_color=("gray75", "gray30"), fg_color=("#e5e5e5", "#353535"), compound="top", text_font=(settings.code_injection['style']['font'], 12), command=self.ping_test)
        self.img.image = _img
        self.img.pack(side="left", padx=5)

        ci.CTkButton(self.item_frame, width=110, height=90, text="", hover_color=("#DEDEDE", "#2E2E2E"), fg_color=("#DEDEDE", "#2E2E2E")).pack(side="left", padx=5)
        ci.CTkButton(self.item_frame, width=110, height=90, text="", hover_color=("#DEDEDE", "#2E2E2E"), fg_color=("#DEDEDE", "#2E2E2E")).pack(side="left", padx=5)
        ci.CTkButton(self.item_frame, width=110, height=90, text="", hover_color=("#DEDEDE", "#2E2E2E"), fg_color=("#DEDEDE", "#2E2E2E")).pack(side="left", padx=5)
