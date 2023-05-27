import subprocess
import threading
import time
from enum import Enum
from ui.test.record.Util import TFile
from adbutils import AdbDevice, AdbClient, adb, adb_path

_device = None
_device_name = None

def get_device_list():
    devices = []
    for device in adb.device_list():
        if isinstance(device, AdbDevice):
            if device.serial not in devices:
                devices.append(device.serial)
                #print("接入设备：{}".format(device.serial))
    return devices


def get_device_ip(device):
    cmds = [adb_path(), "-s", device, "shell", "ip", "route"]
    output = subprocess.run(cmds, timeout=15, stdout=subprocess.PIPE).stdout.decode("utf-8")
    if output == "":
        return ""
    ip = output.split("src ")[1].split(" ")[0]
    return ip


def get_device_ip_dict():
    device_dict = {}
    devices = get_device_list()
    for d in devices:
        if not d.count('.'):
            ip = get_device_ip(d)
            device_dict[d] = ip
        else:
            device_dict[d] = ''
    return device_dict


def get_device_status(device_name):
    try:
        adb.device(device_name).send_keys('')
    except Exception as e:
        return False
    return True


def start_tcpip(device):
    cmds = ['adb', "-s", device, "tcpip", "5555"]
    out = subprocess.run(cmds, timeout=5.0)
    return out.returncode
  
def adb_connect(addr=''):
    if addr.count('.') > 0:
        return adb.connect(addr)

def send_key(name):
    global _device
    try:
        if _device is None:
            _device = adb.device(_device_name)
        key = TFile.get_json_key(name,TFile.KEY_PATH)
        _device.keyevent(key)
    except:
        return False
    return True

def click(x,y):
    global _device
    try:
        if _device is None:
            _device = adb.device(_device_name)
        _device.click(x, y)
    except Exception as e:
        print(e)
        return False
    return True
    
def swipe(sx, sy, ex, ey):
    global _device
    if _device is None:
        _device = adb.device(_device_name)
    try:
        _device.swipe(sx, sy, ex, ey)
    except:
        return False
    return True

def app_current_match(activity=None,package=None,match=False):
    global _device
    try:
        if _device is None:
            _device = adb.device(_device_name)
        if not match:
            if activity:
                return _device.app_current().activity
            
            elif package:
                return _device.app_current().package
            
            else:
                return _device.app_current()
        else:
            if activity:
                 if _device.app_current().activity in activity:
                    return True
            if package:
                if _device.app_current().package in package:
                    return True

    except Exception as e:
        print(e)

    return False

def app_start(package_name: str, activity: str):
    global _device
    try:
        if _device is None:
            _device = adb.device(_device_name)
        _device.app_start(package_name=package_name,activity=activity)

    except Exception as e:
        print(e)



def adb_send_key(cmd,match=None,timeout=5):
    p = subprocess.Popen(cmd, shell=True,  stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if match:
        start_time = time.time()
        while time.time() - start_time < timeout:
            line = p.stdout.readline()  # 读取数据
            line = str(line, 'UTF-8')  # byte 转 str
            print(line)
            if line:
                if line.count(match):
                    return True
        return False
    return True
            


def adb_read(p,match):
    while p.poll() is None:
        line = p.stdout.readline()  # 读取数据
        line = str(line, 'UTF-8')  # byte 转 str
        if line:
            print(line)
            if match.count(line) >0:
                return






    
    


