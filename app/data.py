class UserData:
    __instance = None

    @staticmethod
    def get_instance():
        return UserData.__instance

    def __init__(self):
        UserData.__instance = self
        self.user_name = None

    def set_id(self, id):
        self.user_id = id

    def set_name(self, name):
        self.user_name = name

    def set_user(self, user):
        self.user_user = user        

    def set_role(self, role):
        self.user_role = role 

    def set_email(self, email):
        self.user_email = email        

    def set_pwmd5(self, password):
        self.user_pwmd5 = password 

    def set_bk_name(self, bk_name):
        self.user_bk_name = bk_name 

    def set_avatar(self, avatar):
        self.user_avatar = avatar   
