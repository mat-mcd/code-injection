import tkinter, threading, requests, cryptocode, time, os, hashlib, re, sys
import customtkinter as ci
from tkinter import ttk, filedialog, messagebox, PhotoImage
from datetime import datetime
from datetime import timedelta
from app import settings
from app import data
from PIL import Image, ImageTk
from app import logs
from tkinter.messagebox import askyesno

class myaccount(ci.CTkFrame):
    def __init__(self, master):
        self.master = master
        self.user_data = data.UserData.get_instance()
        style = ttk.Style()
        style.theme_use("clam")
        self.create_content()

    def reset_device(self, device, serial):
        if settings.check_network():
            answer = askyesno(title='Aviso do Sistema', message=f'O dispositivo {device} será desviculado da sua licença\nDeseja continuar?')
            if answer:                
                serial_decrypt = cryptocode.decrypt(serial, settings.secret_key)
                user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36"
                headers = {
                    "User-Agent": user_agent
                }
                requests.get(settings.url_check_license+f'get-device.php?serial={serial_decrypt}&device_id=0&device_name=0', headers=headers)
                
                data_sql = ["0","0","0"]
                settings.c.execute("UPDATE settings set serial_license=?, device_id=?, device_name=?", data_sql)
                settings.db.commit()
                messagebox.showinfo("Aviso do Sistema", f'O dispositivo {device} foi desviculado da sua licença')
                os.execl(sys.executable, os.path.abspath(__file__), *sys.argv)
        else:
            messagebox.showinfo('Aviso do Sistema', 'Você precisa está conectado a internet para resetar o dispositivo vinculado a sua licença')

                    
    def thread_license(self):
        pr=threading.Thread(target=self.update_license)
        pr.start()

    def update_license(self):
        self.txt_license.configure(text='Atualizando...', state='disabled')
        try:
            fetch = settings.c.execute("SELECT * FROM settings")
            rows = fetch.fetchone()
            decrypt_client_id = cryptocode.decrypt(rows[0], settings.secret_key)
            user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36"
            headers = {
                "User-Agent": user_agent
            }
            r = requests.get(settings.url_check_license+f'check-license.php?serial={decrypt_client_id}', headers=headers)
            result = r.json()  
            add_days = (datetime.now() + timedelta(days=settings.check_lincese_days) ).strftime('%d/%m/%Y %H:%M:%S')
            data_sql = str(cryptocode.encrypt(add_days, settings.secret_key))

            get_client_name = str(cryptocode.encrypt(result['name'], settings.secret_key))
            get_tel = str(cryptocode.encrypt(result['contact2'], settings.secret_key))
            get_phone = str(cryptocode.encrypt(result['contact1'], settings.secret_key))
            get_cpf_cnpj = str(cryptocode.encrypt(result['cpf_cnpj'], settings.secret_key))
            get_license = str(cryptocode.encrypt(result['expiration'], settings.secret_key))
            get_plan = str(cryptocode.encrypt(result['plan'], settings.secret_key))
            last_check_license = str(cryptocode.encrypt(time.strftime("%d/%m/%Y %H:%M:%S"), settings.secret_key))
            data_update = (data_sql,get_client_name,get_tel,get_phone,get_cpf_cnpj,get_license,get_plan,last_check_license)

            settings.c.execute("UPDATE settings set next_update=?, get_name=?, get_tel=?, get_phone=?, get_cpf_cnpj=?, get_license=?, get_plan=?, last_check_license=?", data_update)
            settings.db.commit()
            messagebox.showinfo("Aviso do Sistema", 'As informações da sua licença foi atualizada com sucesso!\n\nAtualize a página para visualizar as alterações')
                     

        except requests.exceptions.HTTPError as errh:
            messagebox.showinfo("Aviso do Sistema",'Erro na comunicação com o servidor de licença\n\n'+str(errh))
        except requests.exceptions.ConnectionError:
            messagebox.showinfo("Aviso do Sistema",'Erro na comunicação com o servidor de licença\nVerifique sua conexão com a internet')
        except requests.exceptions.Timeout:
            messagebox.showinfo("Aviso do Sistema",'Erro na comunicação com o servidor de licença\nError: Timeout')
        except requests.exceptions.RequestException as err:
            messagebox.showinfo("Aviso do Sistema",'Resposta inválida do servidor de licença\n\n'+str(err)) 
        self.txt_license.configure(text='Atualizar', state='enabled')    

    def update_account(self):
        regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        str_fullname = self.fullname.get()
        str_email = self.email.get()
        str_username = self.username.get()
        str_new_password = self.new_password.get()
        str_password = self.password.get()
        str_backup = self.backup.get()
        password_insert = ''

        str_password_md5 = hashlib.md5(settings.prefix_password+str_password.encode('utf8')).hexdigest()

        if str_fullname == '':
            messagebox.showinfo("Aviso do Sistema", "Informe seu nome & sobrenome", parent=self.win)
        elif str_email == '':
            messagebox.showinfo("Aviso do Sistema", "Informe seu endereço de e-mail", parent=self.win)
        elif str_username == '':
            messagebox.showinfo("Aviso do Sistema", "Informe seu nome de usuário", parent=self.win)
        elif str_password == '':
            messagebox.showinfo("Aviso do Sistema", "Informe seu senha de acesso atual", parent=self.win)
        elif not re.match(regex, str_email):
            messagebox.showinfo("", "Informe um endereço de e-mail válido")
        elif len(str_backup) > 4:
            messagebox.showinfo("Aviso do Sistema", "A singla do backup não pode ter mais de 4 caracteres", parent=self.win)
        elif str_password_md5 != self.user_data.user_pwmd5:
            messagebox.showinfo("Aviso do Sistema", "Senha de acesso atual incorreta", parent=self.win)
        else:
            if str_new_password == "":
                password_insert = self.user_data.user_pwmd5                
            else:
                password_insert = hashlib.md5(settings.prefix_password+str_new_password.encode('utf8')).hexdigest()

            sqliteConnection = settings.db
            cursor = settings.c
            sqlite_insert_query = """UPDATE users SET
                          name='{}', username='{}', email='{}', password='{}', bk_name='{}', role='{}' WHERE id='{}'
                          """.format(str_fullname, str_username, str_email, password_insert, str_backup, self.value_role.get(), self.user_data.user_id)

            cursor.execute(sqlite_insert_query)
            sqliteConnection.commit()

            if settings.dev_mode == False:
                 logs.add.insert_log(self, "Atualizou dados da conta")

            settings.edit_ini('app', 'username', str(str_username))
            messagebox.showinfo("Aviso do Sistema", "Suas configurações foram salvas\n\nO programa será reniciado para aplicar as alterações", parent=self.win)
            os.execl(sys.executable, os.path.abspath(__file__), *sys.argv)

    def edit_user(self):
        self.win = ci.CTkToplevel(self.master)
        self.win.geometry("560x450")
        self.win.iconbitmap(settings.folder_assets+"/img/code-injection.ico")
        self.win.title(f'Editando conta ({self.user_data.user_user}) - {settings.app_name} v{settings.app_version}')
        self.win.columnconfigure(0, weight=1)
        self.win.columnconfigure(1, weight=3)

        frame = ci.CTkFrame(self.win, corner_radius=10, width=500)
        frame.pack(padx=10, pady=20)



        label = ci.CTkLabel(frame, text="Usuário:", text_font=(settings.code_injection['style']['font'], 12))
        label.grid(column=0, row=0, sticky='w', padx=5, pady=10)
        username_value = tkinter.StringVar(frame, value=self.user_data.user_user)
        self.username = ci.CTkEntry(frame, width=365, textvariable=username_value, text_font=(settings.code_injection['style']['font'], 12))
        self.username.grid(column=1, row=0, sticky='e', padx=20, pady=10)

        
        label = ci.CTkLabel(frame, text="E-mail:", text_font=(settings.code_injection['style']['font'], 12))
        label.grid(column=0, row=2, sticky='w', padx=5, pady=10)
        email_value = tkinter.StringVar(frame, value=self.user_data.user_email)
        self.email = ci.CTkEntry(frame, width=365,  textvariable=email_value, text_font=(settings.code_injection['style']['font'], 12))
        self.email.grid(column=1, row=2, sticky='e', padx=20, pady=10)
        
        
        label = ci.CTkLabel(frame, text="Nome:", text_font=(settings.code_injection['style']['font'], 12))
        label.grid(column=0, row=3, sticky='w', padx=5, pady=10)
        fullname_value = tkinter.StringVar(frame, value=self.user_data.user_name)
        self.fullname = ci.CTkEntry(frame, width=365,  textvariable=fullname_value, text_font=(settings.code_injection['style']['font'], 12))
        self.fullname.grid(column=1, row=3, sticky='e', padx=20, pady=10)

     
        label = ci.CTkLabel(frame, text="Sigla Backup:", text_font=(settings.code_injection['style']['font'], 12))
        label.grid(column=0, row=4, sticky='w', padx=5, pady=10)
        backup_value = tkinter.StringVar(frame, value=self.user_data.user_bk_name)
        self.backup = ci.CTkEntry(frame, width=365,  textvariable=backup_value, text_font=(settings.code_injection['style']['font'], 12))
        self.backup.grid(column=1, row=4, sticky='e', padx=20, pady=10)

        self.value_role = tkinter.StringVar(frame)
        self.value_role.set(self.user_data.user_role) 
        label = ci.CTkLabel(frame, text="Função:", text_font=(settings.code_injection['style']['font'], 12))
        label.grid(column=0, row=5, sticky='w', padx=5, pady=10)
        backup_value = tkinter.StringVar(frame, value=self.user_data.user_bk_name)
        self.role = tkinter.OptionMenu(frame, self.value_role, "Técnico", "Administrador")
        self.role.configure(width=36, background=settings.bg_color, fg=settings.text_color, highlightthickness=0, font=(settings.code_injection['style']['font'], 12))
        self.role.grid(column=1, row=5, sticky='e', padx=20, pady=10)

        
        label = ci.CTkLabel(frame, text="Nova Senha:", text_font=(settings.code_injection['style']['font'], 12))
        label.grid(column=0, row=6, sticky='w', padx=5, pady=10)
        self.new_password = ci.CTkEntry(frame, width=365, placeholder_text="Se não deseja alterar deixe este campo em branco", show="*", text_font=(settings.code_injection['style']['font'], 12))
        self.new_password.grid(column=1, row=6, sticky='e', padx=20, pady=10)
        
        
        label = ci.CTkLabel(frame, text="Senha Atual:", text_font=(settings.code_injection['style']['font'], 12))
        label.grid(column=0, row=7, sticky='w', padx=5, pady=10)
        self.password = ci.CTkEntry(frame, width=365, show="*", text_font=(settings.code_injection['style']['font'], 12))
        self.password.grid(column=1, row=7, sticky='e', padx=20, pady=10)
        

        save = ci.CTkButton(frame, width=365, text='Salvar', text_font=(settings.code_injection['style']['font'], 12), command=self.update_account)
        save.grid(column=1, row=8, sticky='e', padx=20, pady=10)


    def update_photo(self):
            messagebox.showinfo('Aviso do Sistema', 'Para atualizar seu avatar clique na sua imagem de perfil no menu principal') 

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    def onFrameConfigure(self,canvas):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def create_content(self):
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

        self.frame = ci.CTkFrame(self.canvas, corner_radius=0)
        
        if settings.code_injection['style']['theme'] == 'dark':
            line_color = 'gray40'
        else:
            line_color = 'gray80'

        ci.CTkLabel(self.frame, height=0, text="").grid()

        self.basic_info = ci.CTkFrame(self.frame, fg_color=("gray75", "gray30"))
        self.basic_info.grid(row=2, column=0, sticky="nswe", padx=20)

        frame = ci.CTkFrame(self.basic_info, height=23, fg_color=("gray75", "gray30"))
        frame.pack(fill="both", padx=20, pady=15)

        ci.CTkLabel(frame, text="INFORMAÇÕES BÁSICAS", height=1, fg_color=("gray75", "gray30"), text_font=("Roboto Medium", 17)).place(relx=0.27)
        ci.CTkFrame(self.basic_info, height=1.2, fg_color=line_color).pack(fill="both", pady=5)

        
        frame = ci.CTkFrame(self.basic_info, fg_color=("gray75", "gray30"))
        frame.pack(fill="both", padx=20)

        title = ci.CTkLabel(frame, text="AVATAR", text_color=settings.hover_color, text_font=("Roboto Medium", -15)).pack(fill="both", side="left")

        if os.path.isfile(settings.folder_assets+'/img/avatar/'+self.user_data.user_avatar):
            image = Image.open(settings.folder_assets+'/img/avatar/'+self.user_data.user_avatar)
            image=image.resize((40,40),Image.ANTIALIAS)
        else:
            image = Image.open(settings.folder_assets+"/img/avatar/avatar.png")
            image=image.resize((40,40),Image.ANTIALIAS)

        self.photo_file = ImageTk.PhotoImage(image)

        self.avatar = ci.CTkButton(master=frame, image=self.photo_file, width=42, text="", fg_color=("gray70", "gray25"), hover_color="gray35", command=self.update_photo)
        self.avatar.pack(fill="both", side="right", padx=40)


        ci.CTkFrame(self.basic_info, height=1.2, fg_color=line_color).pack(fill="both", pady=10)
        



                
        frame = ci.CTkFrame(self.basic_info, fg_color=("gray75", "gray30"))
        frame.pack(fill="both", padx=20)

        ci.CTkLabel(frame, text="ID", text_color=settings.hover_color, text_font=("Roboto Medium", -15)).pack(side="left")
        ci.CTkLabel(frame, text=self.user_data.user_id+" "*50, text_font=(settings.code_injection['style']['font'], -15)).pack(side="left")
        ci.CTkFrame(self.basic_info, height=1.2, fg_color=line_color).pack(fill="both", pady=10)
        

        
        frame = ci.CTkFrame(self.basic_info, fg_color=("gray75", "gray30"))
        frame.pack(fill="both", padx=20)

        ci.CTkLabel(frame, text="USUARIO", text_color=settings.hover_color, text_font=("Roboto Medium", -15)).pack(side="left")
        ci.CTkLabel(frame, text=self.user_data.user_user+" "*50, text_font=(settings.code_injection['style']['font'], -15)).pack(side="left")
        ci.CTkButton(frame, text=">", fg_color=("gray75", "gray30"), command=self.edit_user).pack(side="right")

        ci.CTkFrame(self.basic_info, height=1.2, fg_color=line_color).pack(fill="both", pady=10)
        

        
        frame = ci.CTkFrame(self.basic_info, fg_color=("gray75", "gray30"))
        frame.pack(fill="both", padx=20)

        ci.CTkLabel(frame, text="NOME", text_color=settings.hover_color, text_font=("Roboto Medium", -15)).pack(side="left")
        ci.CTkLabel(frame, text=self.user_data.user_name+" "*50, text_font=(settings.code_injection['style']['font'], -15)).pack(side="left", anchor="w")
        ci.CTkButton(frame, text=">", fg_color=("gray75", "gray30"), command=self.edit_user).pack(side="right")

        ci.CTkFrame(self.basic_info, height=1.2, fg_color=line_color).pack(fill="both", pady=10)
        

        
        frame = ci.CTkFrame(self.basic_info, fg_color=("gray75", "gray30"))
        frame.pack(fill="both", padx=20)

        ci.CTkLabel(frame, text="E-MAIL", text_color=settings.hover_color, text_font=("Roboto Medium", -15)).pack(side="left")
        ci.CTkLabel(frame, text=self.user_data.user_email+" "*30, text_font=(settings.code_injection['style']['font'], -15)).pack(side="left", anchor="w")
        ci.CTkButton(frame, text=">", fg_color=("gray75", "gray30"), command=self.edit_user).pack(side="right")

        ci.CTkFrame(self.basic_info, height=1.2, fg_color=line_color).pack(fill="both", pady=10)
        

        
        frame = ci.CTkFrame(self.basic_info, fg_color=("gray75", "gray30"))
        frame.pack(fill="both", padx=20)

        ci.CTkLabel(frame, text="SENHA", text_color=settings.hover_color, text_font=("Roboto Medium", -15)).pack(side="left")
        ci.CTkLabel(frame, text="*******"+" "*50, text_font=(settings.code_injection['style']['font'], -15)).pack(side="left", anchor="w")
        ci.CTkButton(frame, text=">", fg_color=("gray75", "gray30"), command=self.edit_user).pack(side="right")

        ci.CTkFrame(self.basic_info, height=1.2, fg_color=line_color).pack(fill="both", pady=10)
        

                
        frame = ci.CTkFrame(self.basic_info, fg_color=("gray75", "gray30"))
        frame.pack(fill="both", padx=20)

        ci.CTkLabel(frame, text="FUNÇÃO", text_color=settings.hover_color, text_font=("Roboto Medium", -15)).pack(side="left")
        ci.CTkLabel(frame, text=self.user_data.user_role+" "*50, text_font=(settings.code_injection['style']['font'], -15)).pack(side="left")

        ci.CTkFrame(self.basic_info, height=1.2, fg_color=line_color).pack(fill="both", pady=10)
        

                
        frame = ci.CTkFrame(self.basic_info, fg_color=("gray75", "gray30"))
        frame.pack(fill="both", padx=20)

        ci.CTkLabel(frame, text="BACKUP", text_color=settings.hover_color, text_font=("Roboto Medium", -15)).pack(side="left")
        ci.CTkLabel(frame, text=self.user_data.user_bk_name+" "*50, text_font=(settings.code_injection['style']['font'], -15)).pack(side="left")
        ci.CTkButton(frame, text=">", fg_color=("gray75", "gray30"), command=self.edit_user).pack(side="right")

        ci.CTkFrame(self.basic_info, height=1.2, fg_color=None).pack(fill="both", pady=10)
        


        # /////////////////////////////////////////////////////////////////////////////////////////////////////////

        self.license_info = ci.CTkFrame(self.frame, fg_color=("gray75", "gray30"))
        self.license_info.grid(row=3, column=0, sticky="nswe", padx=20, pady=30)

        frame = ci.CTkFrame(self.license_info, height=27, fg_color=("gray75", "gray30"))
        frame.pack(fill="both", padx=20, pady=15)

        ci.CTkLabel(frame, text="INFORMAÇÕES DA LICENÇA", fg_color=("gray75", "gray30"), text_font=("Roboto Medium", 17)).place(relx=0.245)
        ci.CTkFrame(self.license_info, height=1, fg_color=line_color).pack(fill="both")

        frame2 = ci.CTkFrame(self.license_info, height=1, fg_color=("gray75", "gray30"))
        frame2.pack(fill="both", pady=5)

                
        frame = ci.CTkFrame(self.license_info, fg_color=("gray75", "gray30"))
        frame.pack(fill="both", padx=20)
        fetch = settings.c.execute("SELECT * FROM settings")
        rows = fetch.fetchone()


        ci.CTkLabel(frame, text="NOME", text_color=settings.hover_color, text_font=("Roboto Medium", -15)).pack(side="left")
        ci.CTkLabel(frame, text=cryptocode.decrypt(rows[3], settings.secret_key)+" "*30, text_font=(settings.code_injection['style']['font'], -15)).pack(side="left")

        ci.CTkFrame(self.license_info, height=1.2, fg_color=line_color).pack(fill="both", pady=10)
        


                
        frame = ci.CTkFrame(self.license_info, fg_color=("gray75", "gray30"))
        frame.pack(fill="both", padx=20)


        ci.CTkLabel(frame, text="CPF/CNPJ", text_color=settings.hover_color, text_font=("Roboto Medium", -15)).pack(side="left")
        ci.CTkLabel(frame, text=cryptocode.decrypt(rows[6], settings.secret_key)+" "*30, text_font=(settings.code_injection['style']['font'], -15)).pack(side="left")

        ci.CTkFrame(self.license_info, height=1.2, fg_color=line_color).pack(fill="both", pady=10)
        

                
        frame = ci.CTkFrame(self.license_info, fg_color=("gray75", "gray30"))
        frame.pack(fill="both", padx=20)

        if cryptocode.decrypt(rows[11], settings.secret_key) == "full":
            plan = 'Completo'
        else:
            plan = 'Básico'

        ci.CTkLabel(frame, text="PLANO", text_color=settings.hover_color, text_font=("Roboto Medium", -15)).pack(side="left")
        ci.CTkLabel(frame, text=plan+" "*30, text_font=(settings.code_injection['style']['font'], -15)).pack(side="left")

        ci.CTkFrame(self.license_info, height=1.2, fg_color=line_color).pack(fill="both", pady=10)
        

                
        frame = ci.CTkFrame(self.license_info, fg_color=("gray75", "gray30"))
        frame.pack(fill="both", padx=20)

        ci.CTkLabel(frame, text="CONTATO", text_color=settings.hover_color, text_font=("Roboto Medium", -15)).pack(side="left")
        ci.CTkLabel(frame, text=cryptocode.decrypt(rows[4], settings.secret_key)+' / '+cryptocode.decrypt(rows[5], settings.secret_key)+" "*10, text_font=(settings.code_injection['style']['font'], -15)).pack(side="left")

        ci.CTkFrame(self.license_info, height=1.2, fg_color=line_color).pack(fill="both", pady=10)
        
        frame = ci.CTkFrame(self.license_info, fg_color=("gray75", "gray30"))
        frame.pack(fill="both", padx=20)

        ci.CTkLabel(frame, text="SERIAL", text_color=settings.hover_color, text_font=("Roboto Medium", -15)).pack(side="left")
        ci.CTkLabel(frame, text=cryptocode.decrypt(rows[0], settings.secret_key)+" "*30, text_font=(settings.code_injection['style']['font'], -15)).pack(side="left")

        ci.CTkFrame(self.license_info, height=1.2, fg_color=line_color).pack(fill="both", pady=10)
        

                
        frame = ci.CTkFrame(self.license_info, fg_color=("gray75", "gray30"))
        frame.pack(fill="both", padx=20)


        ci.CTkLabel(frame, text="EXPIRAÇÃO DA LICENÇA  ", text_color=settings.hover_color, text_font=("Roboto Medium", -15)).pack(side="left")
        ci.CTkLabel(frame, text=cryptocode.decrypt(rows[7], settings.secret_key)+" "*15, text_font=(settings.code_injection['style']['font'], -15)).pack(side="left")

        ci.CTkFrame(self.license_info, height=1.2, fg_color=line_color).pack(fill="both", pady=10)


        self.txt_license=ci.CTkButton(frame, text="Atualizar", fg_color=None, text_font=(settings.code_injection['style']['font'], -15), command=self.thread_license)
        self.txt_license.pack()       


                
        frame = ci.CTkFrame(self.license_info, fg_color=("gray75", "gray30"))
        frame.pack(fill="both", padx=20)


        ci.CTkLabel(frame, text="ÚLTIMA ATUALIZAÇÃO     ", text_color=settings.hover_color, text_font=("Roboto Medium", -15)).pack(side="left")
        ci.CTkLabel(frame, text=cryptocode.decrypt(rows[8], settings.secret_key)+" "*30, text_font=(settings.code_injection['style']['font'], -15)).pack(side="left")

        ci.CTkFrame(self.license_info, height=1.2, fg_color=line_color).pack(fill="both", pady=10)
        


                
        frame = ci.CTkFrame(self.license_info, fg_color=("gray75", "gray30"))
        frame.pack(fill="both", padx=20)


        ci.CTkLabel(frame, text="PRÓXIMA ATUALIZAÇÃO  ", text_color=settings.hover_color, text_font=("Roboto Medium", -15)).pack(side="left")
        ci.CTkLabel(frame, text=cryptocode.decrypt(rows[1], settings.secret_key)+" "*20, text_font=(settings.code_injection['style']['font'], -15)).pack(side="left")

        ci.CTkFrame(self.license_info, height=1.2, fg_color=line_color).pack(fill="both", pady=10)


        frame = ci.CTkFrame(self.license_info, fg_color=("gray75", "gray30"))
        frame.pack(fill="both", padx=20)

        ci.CTkLabel(frame, text="DISPOSITIVO VINCULADO", text_color=settings.hover_color, text_font=("Roboto Medium", -15)).pack(side="left")
        ci.CTkLabel(frame, text=cryptocode.decrypt(rows[10], settings.secret_key), text_font=(settings.code_injection['style']['font'], -15)).pack(side="left")

        ci.CTkFrame(self.license_info, height=1.2, fg_color=None).pack(fill="both", pady=10)
    

        self.remove_device=ci.CTkButton(frame, text="Desvilcular", fg_color="#ed2a2a", hover_color="#ed0404", text_font=(settings.code_injection['style']['font'], -15), command=lambda:self.reset_device(cryptocode.decrypt(rows[10], settings.secret_key), rows[0]))
        self.remove_device.pack()


        self.frame.bind("<Configure>", lambda event, canvas=self.canvas: self.onFrameConfigure(self.canvas))
        self.canvas.create_window(0, 0, anchor='nw', window=self.frame)
        self.canvas.update_idletasks()
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        self.canvas.configure(scrollregion=self.canvas.bbox('all'),yscrollcommand=scroll_y.set)                         
        self.canvas.pack(expand=True, side='left', pady=20)
        scroll_y.pack(fill='y', side='right',pady=20)