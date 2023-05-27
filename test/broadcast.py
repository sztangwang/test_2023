import adbutils

from utils.adbsocket import DUtils

if __name__ == '__main__':
    for device in adbutils.adb.device_list():
        print(device.serial)
        # adbutils.adb.reverse(device.serial, "tcp:9100", "tcp:9100", True)
        agent = DUtils(device)
        agent.sendBroadcast("com.hollyland.action.ADB_CONNECTED")
