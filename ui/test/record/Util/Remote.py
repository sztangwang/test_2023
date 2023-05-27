
import re
import serial
import time
from ui.test.record.Util import TFile

from serial.tools.list_ports_windows import comports

_Ac = None

def get_ac_port():
    port_list = list(comports())
    ac_port = None
    if port_list:
        for p in port_list:
            if str(p).count('2303') != 0:
                ac_port = (re.findall(r"COM(.+?) ", str(p))[0])
                return ac_port
    return ac_port


def get_ac_serial():
    global _Ac
    if _Ac is None:
        ac_port = get_ac_port()
        print(ac_port)
        try:
            _Ac  = serial.Serial(port="COM"+ac_port, baudrate=9600)
        except Exception as e:
            print('usb异常',e)
            return
    return _Ac
   
def ac_off(timeout=1):
    global _Ac
    ac_serial = get_ac_serial()
    if not ac_serial:
        return False
    ac_off_key = TFile.get_json_key("断电",TFile.KEY_PATH)
    try:
        ac_serial.write(bytes.fromhex(ac_off_key))
    except:
        _Ac = None
        return False
    return True



def ac_on(timeout=1):
    global _Ac
    ac_serial = get_ac_serial()
    if not ac_serial:
        return False
    ac_on_key = TFile.get_json_key("上电",TFile.KEY_PATH)
    try:
        ac_serial.write(bytes.fromhex(ac_on_key))
    except:
        _Ac = None
        return False
    return True


   
def usb_off(timeout=1):
    global _Ac
    ac_serial = get_ac_serial()
    if not ac_serial:
        return False
    ac_off_key = TFile.get_json_key("断usb",TFile.KEY_PATH)
    try:
        ac_serial.write(bytes.fromhex(ac_off_key))
    except:
        _Ac = None
        return False
    return True

  

def usb_on(timeout=1):
    global _Ac
    ac_serial = get_ac_serial()
    if not ac_serial:
        return False
    ac_on_key = TFile.get_json_key("接usb",TFile.KEY_PATH)
    try:
       ac_serial.write(bytes.fromhex(ac_on_key))
    except:
        _Ac = None
        return False
    return True


def power():
    global _Ac
    ac_serial = get_ac_serial()
    if not ac_serial:
        return False
    power_key = str(TFile.get_json_key("power键",TFile.KEY_PATH)).split('，')
    try:
        ac_serial.write(bytes.fromhex(power_key[0]))
        time.sleep(3)
        ac_serial.write(bytes.fromhex(power_key[1]))
    except:
        _Ac = None
        return False
    
    return True


