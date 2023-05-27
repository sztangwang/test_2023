import subprocess
import threading
import time
import re
import adbutils
import ntplib
from adbutils import *
from dateutil import parser
from msg.adbSocketMessage import SocketMessage, SocketData



def get_device_list():
    devices = []
    for device in adb.device_list():
        if isinstance(device, AdbDevice):
            if device.serial not in devices:
                devices.append(device.serial)
                #print("接入设备：{}".format(device.serial))
    return devices


# 获取网络adb 设备号
def get_connect_device():
    devices = adb.device_list()
    print("当前设备列表：{}".format(devices))
    if len(devices) <= 0:
        logger.error("没有设备")
        return
    for device in devices:
        device_connect = get_ip_port(device.serial)
        cmds = [adb_path(), "-s", device.serial, "tcpip", "5555"]
        print("cmds:{}".format(cmds))
        out = subprocess.run(cmds, timeout=5.0)
        if out.returncode != 0:
            logger.error("设备{}启动adb tcpip失败".format(device.serial))
            return
        else:
            print("设备{}启动adb tcpip成功".format(device.serial))

        cmds1 = [adb_path(), "-s", device.serial, "connect", device_connect]
        out1 = subprocess.run(cmds1, timeout=5.0)
        time.sleep(5)
        if out1.returncode != 0:
            logger.error("设备{}连接网络adb失败".format(device.serial))
            return None
        else:
            print("设备{}连接网络adb成功".format(device.serial))
            # 重新获取设备列表
            for d in adb.device_list():
                if d.serial == device_connect:
                    print("设备{}已连接".format(d.serial))
                    device_serial = d.serial
                    return device_serial
            return None


def get_device_ip(device):
    # 使用 adb shell ip route 命令查询设备的 IP 地址
    cmds = [adb_path(), "-s", device, "shell", "ip", "route"]
    print("deg_device_ip-cmds---->:{}".format(cmds))
    output = subprocess.run(cmds, timeout=15, stdout=subprocess.PIPE).stdout.decode("utf-8")
    if output == "":
        return None
    ip = output.split("src ")[1].split(" ")[0]
    time.sleep(5)
    return ip


def get_devices_ip(device):
    # 获取ip地址+5555端口号
    ip = get_device_ip(device)
    if ip is None:
        return None
    else:
        ip = ip + ":5555"
    return ip


# 断开网络adb
def disconnect_device():
    devices = adb.device_list()
    if len(devices) <= 0:
        logger.error("没有设备")
        return
    for device in devices:
        cmds = [adb_path(), "-s", device.serial, "disconnect", device_connect]
        out = subprocess.run(cmds, timeout=5.0)
        try:
            if out.returncode != 0:
                logger.error("设备{}断开网络adb失败".format(device.serial))
                return
            else:
                print("设备{}断开网络adb成功".format(device.serial))
                break
        except Exception as e:
            logger.error("设备{}断开网络adb失败".format(device.serial))


# 时间对比
def time_compare(device, delta_time):
    """
    比较设备时间与服务器时间
    @param device:  设备对象
    @param delta_time: 时间差值
    @return:
    """
    print("output = device.shell([])")
    output = device.shell(["date"])
    device_time = output.strip()
    tzinfos = {"CST": 28800}
    # 使用python-dateutil.parser解析日期字符串
    device_datetime = parser.parse(device_time, tzinfos=tzinfos)
    # 将设备时间转换为时间戳
    device_timestamp = time.mktime(device_datetime.timetuple())
    # 从 NTP 服务器获取网络时间
    ntp_client = ntplib.NTPClient()
    response = ntp_client.request('pool.ntp.org')
    # 获取网络时间戳
    network_time = response.tx_time
    # 获取服务器时间戳
    server_timestamp = network_time
    # 计算设备时间与服务器时间的差值, 单位为秒
    time_diff = server_timestamp - device_timestamp

    # 输出设备时间、服务器时间和时间差值
    print("Device time:", device_time)
    print("Server time:", time.strftime("%a %b %d %H:%M:%S %Z %Y", time.localtime(server_timestamp)))
    print("Time difference:", time_diff)

    if abs(time_diff) > delta_time:
        print("Time not synchronized")
        return False
    else:
        print("Time synchronized")
        return True


# 检测crash log
def check_crash_log(device):
    """
    检测设备上是否存在crash log
    @param device: 设备对象
    @return:
    """
    activitys = get_dumpsys_activitys(device)
    # 将这个列表中的包名 按照 " | " 连接起来
    # 如果列表只有一个元素，那么就不会有 " | " 连接起来
    if len(activitys) > 1:
        package_list = " | ".join(activitys)
    else:
        package_list = activitys[0]
    print("package_list:{}".format(package_list))

    device.shell("logcat -v time | grep -i 'FATAL|ERROR| EXCEPTION' > /sdcard/crash.log")



# 获取dumpsys activity activities
def get_dumpsys_activitys(device):
    output = device.shell("dumpsys activity activities")
    print("activity:{}".format(output))
    # 使用正则表达式匹配 TaskRecord 中的 A 值
    pattern = re.compile(r'TaskRecord{.*?A=([^,\s]+).*?}', re.DOTALL)
    matches = pattern.findall(output)
    # 输出匹配到的 A 值
    list_package_list = []
    for a in matches:
        if a not in list_package_list:
            list_package_list.append(a)
    return list_package_list


class FactoryAdbSocket:

    def __init__(self, device: AdbDevice):
        self.device = device
        self._ERROR_SERVICE_NOT_INSTALL = "Error: Not found; no service started"
        self._ERROR_NOTHING_SERVICE = "(nothing)"
        self._ERROR_NOTHING_WINDOW = "null"
        self.fullData = []

    @staticmethod
    def socketBroadcast(device, timeout=10):
        # 把设备号转换为AdbDevice
        adbDevice = adb.device(device)
        # agent = FactoryAdbSocket(adbDevice)

        adbDevice.shell(
            "am broadcast -n com.hollyland.hardwaretest/.receiver.AndroidDebugBridgeReceiver"
            "-a {} --ei timeout {}".format("com.hollyland.action.ADB_CONNECTED_START_REBOOT", timeout))
        print(
            "发送广播：：：：：：：：：{} ".format("am broadcast -n com.hollyland.hardwaretest/.receiver.AndroidDebugBridgeReceiver "
                                      "-a com.hollyland.action.ADB_CONNECTED_START_REBOOT --ei timeout 10"))

    def startSocketActivity(self):
        response = self.device.shell(
            ['am', 'start', '-n', "com.hollyland.production.test" + "/" + ".MainFactoryActivity"])
        if "Error" in response:
            return False
        return True

    def is_socket_window_start(self):
        cmd = ["dumpsys", "window"]
        input = self.device.shell(cmd)
        for line in iter(input.splitlines()):
            if "mCurrentFocus" in line:
                if "com.hollyland.cameralive.ui.CameraLiveMainActivity" in line:
                    return True
        return False

    def start_reboot_edl(self):
        print("进入烧录的设备是：{0},执行命令：adb -s {1} reboot edl".format(self.device.serial, self.device.serial))
        self.device.adb_output("reboot","edl")
        # self.device.adb_output("shell","")

    def is_socket_service_start(self):
        # 使用 adb shell dumpsys window | grep mCurrentFocus 查看当前的Activity
        cmd = ["dumpsys", "activity", "|", "grep","com.hollyland.cameralive"]
        input = self.device.shell(cmd)
        if self._ERROR_NOTHING_SERVICE in input:
            return False
        else:
            return True

    def isSocketServiceStart(self):
        cmd = ["dumpsys", "activity", "services", "|", "grep",
               ".service.WorkService"]
        input = self.device.shell(cmd)
        if self._ERROR_NOTHING_SERVICE in input:
            return False
        else:
            return True

    # 传入action 和超时时间
    def sendBroadcast(self, action, timeout=20):
        """
        发送广播
        @param action:
        @param timeout:
        @return:
        """
        print("发送广播：：：：：：：：：{} ".format(action))
        self.device.shell(
            "am broadcast -n com.hollyland.hardwaretest/.receiver.AndroidDebugBridgeReceiver"
            "-a {} --ei timeout {}".format(action, timeout))

    def sendBroadcast(self, action, info_type=None, key=None, value=None):
        """

        @param action:
        @param info_type: --es --ei
        @param key:
        @param value:
        """
        infos = [info_type, key, value]
        if None not in infos:
            return self.device.shell(
                "am broadcast -n com.hollyland.hardwaretest/.receiver.AndroidDebugBridgeReceiver "
                "-a {} {} {} '{}'".format(action, info_type, key, value))
        elif None in infos and (info_type is not None or key is not None
                                or value is not None):
            pass
        else:
            return self.device.shell(
                "am broadcast -n com.hollyland.hardwaretest/.receiver.AndroidDebugBridgeReceiver "
                " -a {}".format(action))

    def isServiceInstalled(self):
        """
        服务是否安装
        @rtype: object
        """
        for app in self.device.list_packages():
            if "com.hollyland.production.test" in app:
                return True
        return False

    def startADBSocketService(self):
        """
        开启应服务
        :return:
        """
        try:
            cmd = ["am", "startservice", "-n",
                   "com.hollyland.production.test/com.hollyland.production.test.service.WorkService"]
            input = self.device.shell(cmd)
            if self._ERROR_SERVICE_NOT_INSTALL in input:
                return False
            else:
                return True
        except AdbError as e:
            print(e)
            return False

    def stopADBSocketService(self):
        """
        关闭服务
        """
        try:
            cmd = ["am", "stopservice",
                   "com.hollyland.production.test/com.hollyland.production.test.service.WorkService"]
            input = self.device.shell(cmd)
            if self._ERROR_SERVICE_NOT_INSTALL in input:
                return False
            else:
                return True
        except AdbError as e:
            print(e)
            return False

    def combine(self, message: SocketMessage):
        """
        字节头尾拼接
        :param message:
        :return:
        """
        head = "AA AA AA AA"
        tail = "FF FF FF FF"
        return bytes.fromhex(head) + bytes(SocketMessage.to_json(message), "utf-8") + bytes.fromhex(tail)

    def socketMessageDecoder(self, response: bytes):
        """
        去除粘包
        :param response:
        :return:
        """
        head = "AA AA AA AA"
        tail = "FF FF FF FF"
        # 不粘包
        if response.startswith(bytes.fromhex(head)) and response.endswith(bytes.fromhex(tail)):
            return response.strip(bytes.fromhex(head)).strip(bytes.fromhex(tail))
        # 头包
        elif response.startswith(bytes.fromhex(head)) and not response.endswith(bytes.fromhex(tail)):
            self.fullData.append(response.strip(bytes.fromhex(head)))
            return self.fullData[0]
        # 尾包
        elif response.endswith(bytes.fromhex(tail)) and not response.startswith(bytes.fromhex(head)):
            self.fullData.append(response.strip(bytes.fromhex(tail)))
            byte_buffer = None
            for buffer in self.fullData:
                byte_buffer += buffer
            self.fullData.clear()
            return byte_buffer
        # 中间包
        elif not response.startswith(bytes.fromhex(head)) and not response.endswith(bytes.fromhex(tail)):
            if response.decode("utf-8") == "":
                return "null".encode("utf-8")
            self.fullData.append(response)
            byte_buffer = None
            for buffer in self.fullData:
                byte_buffer += buffer
            return byte_buffer

    def forward2ADBService(self):
        """
        forward 9000端口
        :return:
        """
        return self.device.forward("tcp:8000", "tcp:9000")

    def getImageFile(self, imageFrom, imageTo):
        """
        获取文件
        :param imageFrom: Android文件位置
        :param imageTo: 存放地址
        :return:
        """
        return self.device.sync.pull(imageFrom, imageTo)

    def sendMessage(self, message: SocketMessage):
        """
        发送消息
        :param d: adb设备
        :param message:消息体
        """
        try:
            data = SocketData(version="1.0", type=1, contents=None)
            head = SocketMessage(cmd=0, data=data)
            client = self.device.create_connection(Network.TCP, 9000)
            print("create connection")
            # 超时
            client.settimeout(20)
            # 握手
            client.send(self.combine(head))
            print("发送消息：{}".format(SocketMessage.to_json(message)))
            print(self.socketMessageDecoder(client.recv(1024)))
            time.sleep(2)
            client.send(self.combine(message))
            response = self.socketMessageDecoder(client.recv(1024))
        except adbutils.errors.AdbError as e:
            return ""
        except TimeoutError as e:
            return "timeout"
        else:
            client.close()
            return response.decode('utf-8')

    def create_connection(self, port):
        """
        创建连接
        :param port:
        :return:
        """
        # print("create connection")
        client = self.device.create_connection(Network.TCP, port)
        # client.settimeout(20)
        return client

    def sendHeadMessage(self, client):
        data = SocketData(version="1.0", type=1, contents=None)
        head = SocketMessage(cmd=0, data=data)
        # 握手
        client.send(self.combine(head))
        self.socketMessageDecoder(client.recv(1024))

    def sendMessage1(self, client, message: SocketMessage):
        """
        发送消息
        :param d: adb设备
        :param message:消息体
        """
        try:
            client.send(self.combine(message))
            print("发送消息：{}".format(SocketMessage.to_json(message)))
            response = self.socketMessageDecoder(client.recv(1024))
            print("响应消息：{}".format(response.decode('utf-8')))
        except adbutils.errors.AdbError as e:
            return ""
        except TimeoutError as e:
            return "timeout"
        return response.decode('utf-8')

    def kill_port(self, port):
        """
        删除特定端口
        :param port:
        :return:
        """
        find_port = 'netstat -aon | findstr %s' % port
        result = os.popen(find_port)
        text = result.buffer.read().decode('utf-8').strip()
        # print("text:" + text)
        pid = text[-5::]
        find_kill = 'taskkill -f -pid %s' % pid
        # print(find_kill)
        result = os.popen(find_kill)
        return result.buffer.read()


if __name__ == '__main__':
    devices =get_device_list()
    print(devices)
   
