import sqlite3
from app import data
from app import settings

class add:
    @staticmethod
    def insert_log(self,acao):
            try:
                self.user_data = data.UserData.get_instance()
                sqliteConnection = settings.db
                cursor = settings.c
                #print("successfully connected to database")
                sqlite_insert_query = """INSERT INTO logs
                          (user, action, date, serial_hd, pc_username, pc_name, pc_system) 
                           VALUES 
                          ('{}', '{}', '{}', '{}', '{}', '{}', '{}')""".format(self.user_data.user_user, acao, settings.now.strftime("%d/%m/%Y %H:%M:%S"), settings.serial_number(), settings.pc_username, settings.pc_name, settings.system)

                cursor.execute(sqlite_insert_query)
                sqliteConnection.commit()
                #print("Record inserted successfully into logs table ",cursor.rowcount,)
                #cursor.close()

            except sqlite3.Error as error:
                print("Failed to insert data into database", error)

