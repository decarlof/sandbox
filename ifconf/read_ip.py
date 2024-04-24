import platform
import json
import subprocess

# Get computer name and IP addresses
uname = platform.uname()
local_hostname = uname.node

# print(uname, local_hostname)
if uname.system == "Linux":
    iface_info = json.loads(subprocess.run(['ip', '-j', '-4', 'addr'], capture_output=True).stdout.decode())
    local_ip_list = [iface['addr_info'][0]['local'] for iface in iface_info]
elif uname.system == "Windows":
    s = subprocess.run(['ipconfig', '/allcompartments'], capture_output=True).stdout.decode()
    local_ip_list = [x.split(' ')[-1] for x in s.split('\r\n') if x.strip().startswith('IPv4')]
elif uname.system == "Darwin":
    ip = str(subprocess.check_output(["ifconfig | grep inet"], shell=True)[:-2], 'UTF-8')
    local_ip_list = [x.split(' ')[1] for x in ip.split('\t') if x.split(' ')[0] == 'inet']
else:
    raise RuntimeError(f'Unknown system platform {uname.system}')

print(local_ip_list)
