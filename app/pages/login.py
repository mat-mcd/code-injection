import tkinter, datetime, hashlib, time, sys, cryptocode, requests, os, sys, threading
from tkinter import messagebox
import customtkinter as ci
from PIL import Image, ImageTk
from app import settings
from app import data 
from datetime import datetime
from datetime import timedelta
from app import logs
import wmi

WMI = wmi.WMI()

class login(ci.CTkFrame):
    def __init__(self, master):
        self.master = master
        self.master.iconbitmap(settings.folder_assets+"/img/code-injection.ico")                
        self.set_data = data.UserData()
        self.create_content()
        self.info = settings.get_device_info()

    def auth(self, event=None):
        name_value = self.username.get()
        password_value = self.password.get()
        encrypt = hashlib.md5(settings.prefix_password+password_value.encode('utf8')).hexdigest()
        if name_value == "" or password_value == "":
            messagebox.showinfo("Aviso do Sistema", "Digite seu nome de usuário e senha de acesso para continuar")
        else:
            settings.edit_ini('app', 'username', str(name_value))
            try:
                login = settings.c.execute("SELECT * FROM users WHERE username='"+name_value+"' AND password='"+encrypt+"'")
                rows = login.fetchall()
                if (len(rows) > 0):
                    for row in rows:
                        self.set_data.set_id(str(row[0]))
                        self.set_data.set_name(str(row[1]))
                        self.set_data.set_user(str(row[2]))
                        self.set_data.set_email(str(row[3]))
                        self.set_data.set_pwmd5(str(row[4]))
                        self.set_data.set_role(str(row[5]))
                        self.set_data.set_bk_name(str(row[7]))
                        self.set_data.set_avatar(str(row[8]))
                        settings.edit_ini('app', 'new_acess', 'true')



                    current_date = time.strftime("%d/%m/%Y %H:%M:%S")
                    d1 = time.strptime(current_date, "%d/%m/%Y %H:%M:%S") 
                    check_next_update = settings.c.execute("SELECT * FROM settings")
                    rows = check_next_update.fetchone()

                    if len(self.info) == 0:
                        messagebox.showerror("Falha crítica", f'Erro ao obter dados do dispostivo\nEntre em cotanto com o suporte')
                        sys.exit(1)

                    serial_device = cryptocode.decrypt(rows[9], settings.secret_key)

                    if serial_device != self.info[1] and settings.dev_mode == False:
                        messagebox.showerror("Aviso do Sistema", f'Esta licença já foi vinculada a outro dispositivo\n\nFaça login no dispositovo onde sua licença foi ativada para desvincular ou entre em cotanto com o suporte')
                        sys.exit(1)   
           

                    try:                        
                        decrypt_datetime = cryptocode.decrypt(rows[1], settings.secret_key)
                        decrypt_datetime = time.strptime(decrypt_datetime, "%d/%m/%Y %H:%M:%S") 
                    except Exception as e:
                        messagebox.showerror("Aviso do Sistema", f'Falha ao ler o datetime (next_update) criptografado no banco de dados\n\nContate o suporte para mais informações\n\n{e}')
                        sys.exit(1)

                    try:
                        last_login = cryptocode.decrypt(rows[2], settings.secret_key)
                        last_login = time.strptime(last_login, "%d/%m/%Y %H:%M:%S")
                    except Exception as b:
                        messagebox.showerror("Aviso do Sistema", f'Falha ao ler o datetime (last_login) criptografado no banco de dados\n\nContate o suporte para mais informações\n\n{b}')
                        sys.exit(1)

                    if d1 < last_login:
                        messagebox.showerror("Aviso do Sistema", 'A data e hora do seu computador parece não está correta, corriga e tente novamente\n\nSe esta mensagem persistir entre em contato com o suporte')
                        try:
                            os.system('timedate.cpl')
                        except:
                            pass
                        sys.exit(1)

                    data = time.strftime("%d/%m/%Y %H:%M:%S")
                    data = str(cryptocode.encrypt(data, settings.secret_key))
                    settings.c.execute("UPDATE settings set last_login=?", [data])
                    settings.db.commit()



                    if d1 > decrypt_datetime:
                        if settings.check_network():
                            try:
                                decrypt_client_id = cryptocode.decrypt(rows[0], settings.secret_key) 
                                user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36"
                                headers = {
                                    "User-Agent": user_agent
                                }                 
                                r = requests.get(settings.url_check_license+f'check-license.php?serial={decrypt_client_id}', headers=headers)
                                result = r.json()

                                counts = settings.c.execute("SELECT * FROM users")
                                totals = counts.fetchall()
                                totals = len(totals)

                                current_date = time.strftime("%d/%m/%Y %H:%M:%S")
                                d2 = time.strptime(result['expiration'], "%d/%m/%Y %H:%M:%S")

                                if d1 < d2:
                                    #license up to date, update the date of the next update
                                    add_days = (datetime.now() + timedelta(days=settings.check_lincese_days) ).strftime('%d/%m/%Y %H:%M:%S')
                                    data = str(cryptocode.encrypt(add_days, settings.secret_key))

                                    get_client_name = str(cryptocode.encrypt(result['name'], settings.secret_key))
                                    get_tel = str(cryptocode.encrypt(result['contact2'], settings.secret_key))
                                    get_phone = str(cryptocode.encrypt(result['contact1'], settings.secret_key))
                                    get_cpf_cnpj = str(cryptocode.encrypt(result['cpf_cnpj'], settings.secret_key))
                                    get_license = str(cryptocode.encrypt(result['expiration'], settings.secret_key))
                                    get_plan = str(cryptocode.encrypt(result['plan'], settings.secret_key))
                                    last_check_license = str(cryptocode.encrypt(time.strftime("%d/%m/%Y %H:%M:%S"), settings.secret_key))
                                    data = (data,get_client_name,get_tel,get_phone,get_cpf_cnpj,get_license,get_plan,last_check_license)

                                    settings.c.execute("UPDATE settings set next_update=?, get_name=?, get_tel=?, get_phone=?, get_cpf_cnpj=?, get_license=?, get_plan=?, last_check_license=?", data)
                                    settings.db.commit()
                                    messagebox.showinfo("Aviso do Sistema", f'Sua licença foi ativada com sucesso!\n\nUma nova verificação será realizada em {add_days}')
                                    self.logged = True
                                    for i in self.master.winfo_children():
                                        i.destroy()
                                    self.master.create_base()
                                    self.master.unbind('<Return>')

                                else:
                                    messagebox.showerror("Aviso do Sistema", 'Sua licença expirou\nData da expiração: '+result['expiration']+'\n\nEntre em contato com o suporte para mais informações')

                            except requests.exceptions.HTTPError as errh:
                                messagebox.showerror("Aviso do Sistema",'Erro na comunicação com o servidor de licença\n\n'+str(errh))
                            except requests.exceptions.ConnectionError:
                                messagebox.showerror("Aviso do Sistema",'Erro na comunicação com o servidor de licença\nVerifique sua conexão com a internet')
                            except requests.exceptions.Timeout:
                                messagebox.showerror("Aviso do Sistema",'Erro na comunicação com o servidor de licença\nError: Timeout')
                            except requests.exceptions.RequestException as err:
                                messagebox.showerror("Aviso do Sistema",'Resposta inválida do servidor de licença\n\n'+str(err))
                        else:
                            messagebox.showerror("Aviso do Sistema",'Falha na comunicação com servidor de licença.\nVerifique se você está conectado a internet\n\nO programa realiza uma verificação de licença a cada '+str(settings.check_lincese_days)+' dias\nPor favor, conecte-se a internet e tente novamente')
                    else:
                        self.logged = True
                        for i in self.master.winfo_children():
                            i.destroy()
                        self.master.create_base()
                        self.master.unbind('<Return>')  

                        if settings.dev_mode == False:
                            try:
                                logs.add.insert_log(self, f"Fez login")
                            except:
                                pass
     
                else:
                    messagebox.showerror("Aviso do Sistema", "Desculpe, há um erro com seu usuário ou senha.\n\nCuidado com as teclas shift e caps lock: o sistema diferencia letras maiúsculas e minúsculas")
            except Exception as xd:
                 settings.notification(f'Ocorreu um erro, tente novamente\n{xd}',15)

    def _check_license(self):
        threading.Thread(target=self.check_license).start()

    def check_license(self):
        if self.license.get() == "":
            messagebox.showerror("Aviso do Sistema", "Informe o serial da sua licença")
        elif len(self.license.get()) < 18:
            messagebox.showerror("Aviso do Sistema", "Informe um serial válido\nEx: XXXX-XXXX-XXXX-XXXX")
        else:
            self.btn.configure(text="Validando, aguarde...")
            if settings.check_network():
                try:     
                    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36"
                    headers = {
                        "User-Agent": user_agent
                    }   
                    r = requests.get(settings.url_check_license+f'check-license.php?serial={self.license.get()}',headers=headers)
                    result = r.json()

                    if len(self.info) == 0:
                        messagebox.showerror("Falha crítica", f'Erro ao obter dados do dispostivo\nEntre em cotanto com o suporte')
                        sys.exit(1)

                    if result['device_id'] != self.info[1] and result['device_id'] != "" and result['device_id'] != "0" and settings.dev_mode == False:
                        messagebox.showerror("Aviso do Sistema", 'Esta licença já foi vinculada a outro dispositivo\n\nFaça login no dispositovo onde sua licença foi ativada para desvincular ou entre em cotanto com o suporte')
                        sys.exit(1)  

                    enc = str(cryptocode.encrypt(self.license.get(), settings.secret_key))
                    next_update_now = str(cryptocode.encrypt(time.strftime("%d/%m/%Y %H:%M:%S"), settings.secret_key))

                    info_enc = str(cryptocode.encrypt(self.info[1], settings.secret_key))
                    info_enc2 = str(cryptocode.encrypt(self.info[0], settings.secret_key))

                    data = [enc,next_update_now,info_enc,info_enc2]
                    settings.c.execute("UPDATE settings set serial_license=?, next_update=?, device_id=?, device_name=?", data)
                    settings.db.commit()


                    check_settings = settings.c.execute("SELECT * FROM settings")
                    row = check_settings.fetchall()

                    serial_decrypt = cryptocode.decrypt(row[0][0], settings.secret_key)
                    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36"
                    headers = {
                        "User-Agent": user_agent
                    }  
                    requests.get(settings.url_check_license+f'get-device.php?serial={serial_decrypt}&device_id={self.info[1]}&device_name={self.info[0]}', headers=headers)

                    messagebox.showinfo('Aviso do Sistema', f'Serial aceito pelo servidor de licença!\nO programa será reiniciado para aplicar as novas informações\n\nAtenção: sua licença foi vinculada a este dispositivo:\n{self.info[0]}')
                    os.execl(sys.executable, os.path.abspath(__file__), *sys.argv)

                except requests.exceptions.HTTPError as errh:
                    messagebox.showerror("Aviso do Sistema",'Erro na comunicação com o servidor de licença\n\n'+str(errh))
                except requests.exceptions.ConnectionError:
                    messagebox.showerror("Aviso do Sistema",'Erro na comunicação com o servidor de licença\nVerifique sua conexão com a internet')
                except requests.exceptions.Timeout:
                    messagebox.showerror("Aviso do Sistema",'Erro na comunicação com o servidor de licença\nError: Timeout')
                except requests.exceptions.RequestException as err:
                    settings.notification("Resposta inválida do servidor de licença", 15)
                    messagebox.showerror("Aviso do Sistema",'Resposta inválida do servidor de licença\n'+str(err))
            else:
                settings.notification("Verifique se você está conectado a internet", 15)
                messagebox.showerror("Aviso do Sistema",'Falha na comunicação com servidor de licença.\nVerifique se você está conectado a internet')
            self.btn.configure(text="Tentar novamente")

    def recover_password(self):
        self.get_license = ci.CTkInputDialog(master=self.master, text="Pare resetar sua senha\nDigite o serial da sua licença\nEx: XXXX-XXXX-XXXX-XXXX:", title="Resetar Senha")
        value_dialog = self.get_license.get_input()
        if value_dialog == "":
            messagebox.showinfo("Aviso do Sistema", "Informe o serial da sua licença")
        elif len(value_dialog) < 18:
            messagebox.showinfo("Aviso do Sistema", "Informe um serial válido\nEx: XXXX-XXXX-XXXX-XXXX")
        else:
            if settings.check_network():
                try:
                    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36"
                    headers = {
                        "User-Agent": user_agent
                    }  
                    r = requests.get(settings.url_check_license+f'check-license.php?id={value_dialog}', headers=headers)                    
                    result = r.json()

                    new_password = hashlib.md5(settings.prefix_password+'12345'.encode('utf8')).hexdigest() 
                    settings.c.execute("UPDATE users set password=?", [new_password])
                    settings.db.commit()                        
                    messagebox.showinfo("Senha resetada", "A senha de todos os usuários foram resetados com sucesso!\n\nA nova senha é: 12345\n\nPara sua segurança faça o login e altere agora mesmo!")

                except requests.exceptions.HTTPError as errh:
                    messagebox.showinfo("Aviso do Sistema",'Erro na comunicação com o servidor de licença\n\n'+str(errh))
                except requests.exceptions.ConnectionError as errx:
                    messagebox.showinfo("Aviso do Sistema", f'Erro na comunicação com o servidor de licença\nVerifique sua conexão com a internet\n\n{errx}')
                except requests.exceptions.Timeout:
                    messagebox.showinfo("Aviso do Sistema",'Erro na comunicação com o servidor de licença\nError: Timeout')
                except requests.exceptions.RequestException as err:
                    messagebox.showinfo("Aviso do Sistema",'Resposta inválida do servidor de licença\n\n'+str(err))
            else:
                settings.notification("Verifique se você está conectado a internet", 15)
                messagebox.showinfo("Aviso do Sistema",'Falha na comunicação com servidor de licença\nVerifique se você está conectado a internet')
        
    def new_user(self):
        os.system(f"start \"\" {settings.website}")

    def create_content(self):
        self.master.focus_force()        
        check_settings = settings.c.execute("SELECT * FROM settings")
        row = check_settings.fetchall()

        if row[0][0] == "0" or row[0][0] == "":
            self.master.title(f'Ativação - {settings.app_name}')
            self.master.geometry(f"450x350")


            self.frame = ci.CTkFrame(master=self.master, width=420, height=320)
            self.frame.pack(padx=20, pady=20)


            if settings.code_injection['style']['theme'] == 'dark':
                logo_file = settings.folder_assets+"/img/code-injection[dark].png"
            else:
                logo_file = settings.folder_assets+"/img/code-injection[light].png"

            image = Image.open(logo_file)
            self.bg_image = ImageTk.PhotoImage(image)

            self.logo = ci.CTkLabel(master=self.frame, image=self.bg_image)
            self.logo.image = self.bg_image
            self.logo.place(rely=0.21, relx=0.5, anchor=tkinter.CENTER)


            self.label = ci.CTkLabel(master=self.frame, text=f"Ativação - {settings.app_name} v{settings.app_version}", width=400, text_font=(settings.code_injection['style']['font'], 15))
            self.label.place(rely=0.38, relx=0)

            self.label = ci.CTkLabel(master=self.frame, text=f"Digite o serial da sua licença para continuar", width=400, text_font=(settings.code_injection['style']['font'], 11))
            self.label.place(rely=0.47, relx=0)

            
            self.license = ci.CTkEntry(master=self.frame, corner_radius=20, text_font=(settings.code_injection['style']['font'], 13), width=290, height=37, placeholder_text="      XXXX-XXXX-XXXX-XXXX")
            self.license.place(rely=0.6, relx=0.12)

            self.btn = ci.CTkButton(master=self.frame, corner_radius=20, text="Ativar", text_font=(settings.code_injection['style']['font'], 12), width=290, height=35, command=self._check_license)
            self.btn.place(rely=0.8, relx=0.12)
            

        else:
            self.master.title(f'Login - {settings.app_name} v{settings.app_version}')
            self.master.geometry(f"350x500")

            if settings.code_injection['style']['theme'] == 'dark':
                logo_file = settings.folder_assets+"/img/code-injection[dark].png"
            else:
                logo_file = settings.folder_assets+"/img/code-injection[light].png"

            image = Image.open(logo_file)
            self.bg_image = ImageTk.PhotoImage(image)

            self.frame = ci.CTkFrame(master=self.master,width=350,height=650, corner_radius=0)
            self.frame.place(relx=0.5, rely=0.5, anchor=tkinter.CENTER)

            self.label_1 = ci.CTkLabel(master=self.frame, width=250, height=60, image=self.bg_image)
            self.label_1.place(relx=0.5, rely=0.27, anchor=tkinter.CENTER)

            valuename = tkinter.StringVar(self.frame, value=settings.code_injection['app']['username'])
            self.username = ci.CTkEntry(master=self.frame, text_font=(settings.code_injection['style']['font'], -15), corner_radius=20, width=250, height=37, textvariable=valuename, placeholder_text="usuário")
            self.username.place(relx=0.5, rely=0.45, anchor=tkinter.CENTER)


            if settings.dev_mode:
                value_password = tkinter.StringVar(self.frame, value="12345")
            else:
                value_password = ''

            self.password = ci.CTkEntry(master=self.frame, text_font=(settings.code_injection['style']['font'], -15), corner_radius=20, width=250, height=37, textvariable=value_password, show="*", placeholder_text="senha de acesso")
            self.password.place(relx=0.5, rely=0.53, anchor=tkinter.CENTER)
            self.password.focus()

            self.btnx = ci.CTkButton(master=self.frame, text="Entrar",
                                                    text_font=(settings.code_injection['style']['font'], -15),
                                                    corner_radius=6, command=self.auth, width=250, height=37,)
            self.btnx.place(relx=0.5, rely=0.62, anchor=tkinter.CENTER)


            if settings.dev_mode:
                b1 = tkinter.Button(self.frame, text="dev mode", command=self.auth)
                b1.place(relx=0.5, rely=2)

            

            self.forget = ci.CTkButton(master=self.frame, text='Esqueceu sua senha?', fg_color=("#DEDEDE", "#2E2E2E"), hover_color=None, command=self.recover_password, text_font=(settings.code_injection['style']['font'], -13))
            self.forget.place(relx=0.5, rely=0.72, anchor=tkinter.CENTER)

            self.newaccount = ci.CTkButton(master=self.frame, fg_color=("#DEDEDE", "#2E2E2E"), hover_color=None, text='Não é cliente? crie sua conta', text_font=(settings.code_injection['style']['font'], -13), command=self.new_user)
            self.newaccount.place(relx=0.5, rely=0.76, anchor=tkinter.CENTER)
            self.master.bind("<Return>", self.auth)

            if settings.dev_mode:
                b1.invoke()