import subprocess
from re import sub

disable_terminal = 0x08000000
startupinfo = subprocess.STARTUPINFO()
startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
result = subprocess.Popen('wmic.exe nicconfig where "IPEnabled  = True" get ipaddress,MACAddress,IPSubnet,DNSHostName,Caption,DefaultIPGateway,DNSServerSearchOrder /format:table', shell=True, creationflags=disable_terminal, startupinfo=startupinfo, stdout=subprocess.PIPE) 
data = result.stdout.read().decode('cp850')
data = data.replace('\r', '').strip().split('\n')
del data[0]

networks = ''
for i in data:
    network = i.split('  ')
    for i in range(len(network)):
        try:
            network.remove('')
        except Exception:
            pass    

    name = network[0]
    gateway = network[1].replace('"','').replace('{','').replace('}','')

    try:
        name = network[0]
        gateway = network[1].replace('"','').replace('{','').replace('}','').lstrip()


        ip = network[4].replace('"','').replace('{','').replace('}','')
        mask = network[5].replace('"','').replace('{','').replace('}','')
        mac = network[6]
        dns = network[3].replace('"','').replace('{','').replace('}','')

        name = sub("([\(\[]).*?([\)\]])", "", name).lstrip()
    except:
        pass

    networks+= f'{name}\n    IP:{ip}\n    Máscara:{mask}\n    DNS:{dns}\n    Gateway: {gateway}\n\n'

