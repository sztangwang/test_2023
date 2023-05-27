import subprocess
import time
from adbutils import adb, adb_path

from compoment.atx2agent.core.common.logs.log_uru import Logger

logger = Logger().get_logger



def get_device_ip(device_id):
    time.sleep(1)
    # 使用 adb shell ip route 命令查询设备的 IP 地址
    output = subprocess.run([adb_path(), "-s", device_id, "shell", "ip", "route"], stdout=subprocess.PIPE).stdout.decode(
        "utf-8")
    if output == "":
        return None
    # 解析输出的字符串，获取设备的 IP 地址
    ip = output.split("src ")[1].split(" ")[0]
    return ip

# 获取网络adb 设备号
def get_connect_device():
    devices = adb.device_list()
    logger.info("当前设备列表：{}".format(devices))
    tmp_list = []
    if len(devices) <= 0:
        logger.error("没有设备")
        return
    for device in devices:
        cmd = [adb_path(), "-s", device.serial, "tcpip", "5555"]
        logger.info("cmds:{}".format(cmd))
        out = subprocess.run(cmd, timeout=10.0)
        if out.returncode != 0:
            logger.error("设备{}启动adb tcpip失败".format(device.serial))
            return
        else:
            logger.info("设备{}启动adb tcpip成功".format(device.serial))
            # 连接网络adb 5555端口
            device_connect = get_device_ip(device.serial)
            print("device_connect", device_connect)
            cmd = [adb_path(), "-s", device.serial, "connect", device_connect]
            out1 = subprocess.run(cmd, timeout=10.0)
            if out1.returncode != 0:
                logger.error("设备{}连接网络adb失败".format(device.serial))
                return None
            else:
                logger.info("设备{}连接网络adb成功".format(device.serial))
                device_serial = device_connect
                tmp_list.append(device_serial)
        return tmp_list


# 断开网络adb
def disconnect_device():
    devices = adb.device_list()
    if len(devices) <= 0:
        logger.error("没有设备")
        return
    for device in devices:
        device_connect = get_device_ip(device.serial)
        cmd = [adb_path(), "-s", device.serial, "disconnect", device_connect]
        out = subprocess.run(cmd, timeout=5.0)
        if out.returncode != 0:
            logger.error("设备{}断开网络adb失败".format(device.serial))
            return
        else:
            logger.info("设备{}断开网络adb成功".format(device.serial))
            break

def to_switch_serial(switch_type):
    devices = adb.device_list()
    for device in devices:
        if switch_type == "usb":
            if "." not in device.serial:
                logger.info("切换为usb设备号：{}".format(device.serial))
                device = adb.device(device.serial)
                return device
            else:
                logger.info("没有usb设备号")
                return None
        elif switch_type == "wifi":
            wifi_serial = get_connect_device()
            logger.info("切换为wifi设备号：{}".format(wifi_serial))
            device = adb.device(wifi_serial)
            return device
        else:
            logger.info("设备类型错误")
            return None

def is_network(device):
    """
    判断是否有网络
    @return:
    """
    return "bytes" in device.shell("ping -c 3 www.baidu.com|grep bytes")