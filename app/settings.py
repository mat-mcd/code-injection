import sqlite3, socket, struct, subprocess, winreg, os
import configparser
from tkinter import messagebox
from datetime import datetime
from win10toast import ToastNotifier
import wmi

WMI = wmi.WMI()

app_name = 'Code Injection'
website = 'https://code-injection.com/'


folder_assets = 'assets'

dev_mode = False

prefix_password = b'code-injection_'
secret_key = 'code-injection#8085' 


#license test: 0001-0001-0001-0001
url_check_license = 'https://code-injection.com/update/'
url_changelog = 'https://code-injection.com/changelog.php'
check_lincese_days = 5 
   

#database connection
mysql_host = 'localhost'
mysql_username = 'root'
mysql_password = ''   
mysql_database = 'code_injection'


code_injection = configparser.ConfigParser()
code_injection.read(folder_assets+'/configs/code-injection.ini')


def get_device_info():
    letter = os.getcwd()[:2]
    array = []
    for drive in WMI.Win32_DiskDrive():
        serial = drive.SerialNumber.replace(' ', '')        
        name = drive.Model
        for disk in WMI.query(f'SELECT * FROM Win32_DiskDrive WHERE SerialNumber LIKE "{drive.SerialNumber}"'):
            deviceID = disk.DeviceID
            for partition in WMI.query('ASSOCIATORS OF {Win32_DiskDrive.DeviceID="' + deviceID + '"} WHERE AssocClass = Win32_DiskDriveToDiskPartition'):
                for logical_disk in WMI.query('ASSOCIATORS OF {Win32_DiskPartition.DeviceID="' + partition.DeviceID + '"} WHERE AssocClass = Win32_LogicalDiskToPartition'):
                    if letter == logical_disk.DeviceID:
                        array = [name, serial]
                        return array
                        break

def regedit(locale, name):
    try:
        registry_key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, locale, 0, winreg.KEY_READ)
        value, regtype = winreg.QueryValueEx(registry_key, name)
        winreg.CloseKey(registry_key)
        return value
    except WindowsError:
        return '--'


def replace_line(file_name, line_num, text):
    lines = open(file_name, 'r').readlines()
    lines[line_num] = text
    out = open(file_name, 'w')
    out.writelines(lines)
    out.close()

def check_network():
    try:
        sock = socket.create_connection(("www.google.com", 80), timeout=7)
        if sock is not None:
            sock.close
        return True
    except OSError:
        pass
    return False 

def notification(text, duration=15):
    try:
        ToastNotifier().show_toast(
            f"{app_name} - Notificação",
            f"{text}",
            duration = duration,
            icon_path = folder_assets+"/img/code-injection.ico",
            threaded = True,
        )
    except:
        messagebox.showinfo(f"{app_name} - Notificação", f"{text}")

def edit_ini(section, key, value):
    file_path = folder_assets+'/configs/code-injection.ini'
    config = configparser.ConfigParser()
    config.read(file_path)
    config.set(section,key,value)                         
    cfgfile = open(file_path,'w')
    config.write(cfgfile, space_around_delimiters=False) 
    cfgfile.close()


def terminal(command, call=False): 
    global disable_terminal, startupinfo, notification
    try:
        if call == False:
            process = subprocess.Popen(command, stdin=subprocess.PIPE, creationflags=disable_terminal, stdout=subprocess.PIPE, stderr=subprocess.PIPE, startupinfo=startupinfo, encoding="cp850")
            output, error = process.communicate()
            return str(output)
        else:
            subprocess.call(command, startupinfo=startupinfo, creationflags=disable_terminal)
    except Exception as e:
        notification(f'Ocorreu um erro\n\nSubprocess(terminal)\n{e}', 15)

def serial_number():
    global disable_terminal, startupinfo
    cmd = 'wmic csproduct get uuid'    
    uuid = str(subprocess.check_output(cmd, creationflags=disable_terminal, startupinfo=startupinfo))
    pos1 = uuid.find("\\n")+2
    uuid = uuid[pos1:-15]
    return uuid

def filter(string):
    data = string.stdout.read().decode('cp850')
    data = data.replace('\r', '').strip().split('\n')
    del data[0]
    z = []
    for i in data:
        x = i.split('  ')
        for y in range(len(x)):
            try:
                x.remove('')
            except:
                pass
        z.append(x)
    return z

disable_terminal = 0x08000000
startupinfo = subprocess.STARTUPINFO()
startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

bits = struct.calcsize("P") * 8
now = datetime.now()
app_version = code_injection['app']['version']
system = terminal("Powershell.exe try{(Get-WmiObject Win32_OperatingSystem).Caption}Catch{(Get-CimInstance Win32_OperatingSystem).Caption}").replace('\n', '')
pc_name = socket.gethostname()
pc_username = os.getenv('username')
local_ip = socket.gethostbyname(socket.gethostname())
os_date_install = regedit("SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion",'InstallDate')
os_date_install = datetime.fromtimestamp(os_date_install).strftime("%d/%m/%Y %H:%M:%S")


if code_injection['style']['color'] == "blue":
    hover_color = '#2198d3'
    icon_start = 'play[1].png'

elif code_injection['style']['color'] == "dark-blue":
    hover_color = '#608BD5'
    icon_start = 'play[1].png'
else:
    hover_color = '#0E9670'
    icon_start = 'play[2].png'

if code_injection['style']['theme'] == "dark":
    bg_color = code_injection['style']['bg_dark']
    line_color = '#424141'
    font_color = "gray30"
    text_color = '#E5E5E5'
else:
    bg_color = code_injection['style']['bg_light']
    line_color = '#d1d1d1'
    font_color = "gray75"
    text_color = '#333333'

if not bits:
    version = '32bits'
else:
    version = '64bits'

try:
    db = sqlite3.connect(folder_assets+'/database/system.db',check_same_thread=False)
    c = db.cursor()    
except Exception as e:
    messagebox.showinfo("Aviso do Sistema", e)
