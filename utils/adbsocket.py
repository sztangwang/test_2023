from sre_constants import SUCCESS
import threading
import time

import adbutils
from PyQt5.QtCore import QObject, pyqtSignal, QThread, pyqtSlot
from adbutils import *
import os

from moduel.adbSocketMessage import *
from common.logger import *

logger = Logger(level="info").logger


@dataclass_json
@dataclass
class ADBConnectionData:
    TYPE_IN = 0

    TYPE_OUT = 1

    connectionType: int
    # 连接上的设备
    connected: str
    # 断开的设备
    disConnect: str

    currentDevices: set


@dataclass_json
@dataclass
class NotificationData:
    # 失败
    FAIL_MSG = 0
    # 成功
    SUCCESS_MSG = 1
    # 警告
    WARNING_MSG = 2

    type: int
    info: str
    data: any


class DeviceSignal(QObject):
    # 完成信号
    finished = pyqtSignal()
    # 进度信号
    device = pyqtSignal(object)


class DeviceNotificationThread(QThread):
    # 不可为实例属性

    def __init__(self):
        super().__init__()
        self.devices = set()
        self.pyqtSignal = DeviceSignal()
        self._isStop = False
        self._pause = threading.Event()
        self._pause.set()

    def pause(self):
        logger.info("thread pause()")
        self._pause.clear()

    def resume(self):
        logger.info("thread resume()")
        self._pause.set()

    def stop(self):
        logger.info("thread stop()")
        self._isStop = True
        self.quit()

    def isStop(self):
        return self._isStop

    # 当前只以序列号存储传递搜索到的设备
    def run(self):
        while not self._isStop:
            self._pause.wait()
            time.sleep(2)
            # 有设备连接,但是还没有设备被记录，直接添加
            if len(self.devices) == 0 and len(adbutils.adb.device_list()) > 0:
                for device in adbutils.adb.device_list():
                    self.devices.add(device.serial)
                    self.pyqtSignal.device.emit(ADBConnectionData(connectionType=ADBConnectionData.TYPE_IN,
                                                                  connected=device.serial, disConnect=None,
                                                                  currentDevices=self.devices
                                                                  ))
                    DUtils.socketBroadcast(device)
                self._notify = True
                continue
            # 有设备断开 ,从集合中移除
            if len(adbutils.adb.device_list()) < len(self.devices):
                temps = []
                for connected in adbutils.adb.device_list():
                    temps.append(connected.serial)
                ret = [i for i in self.devices if i not in temps]  # 差集
                for offline in ret:
                    self.pyqtSignal.device.emit(ADBConnectionData(connectionType=ADBConnectionData.TYPE_OUT,
                                                                  connected=
                                                                  None, disConnect=offline, currentDevices=self.devices
                                                                  ))
                    self.devices.remove(offline)
                self._notify = True
                continue
            # 有新的设备连接，添加到集合中
            if len(adbutils.adb.device_list()) > len(self.devices):
                temps = []
                for connected in adbutils.adb.device_list():
                    temps.append(connected.serial)
                ret = [i for i in temps if i not in self.devices]
                for online in ret:
                    self.pyqtSignal.device.emit(ADBConnectionData(connectionType=ADBConnectionData.TYPE_IN,
                                                                  connected=online, disConnect=None,
                                                                  currentDevices=self.devices
                                                                  ))
                    DUtils.socketBroadcast(adbutils.device(online))
                    self.devices.add(online)
                self._notify = True
                continue
            # 无变化,检查下在线和离线的设备
            if len(adbutils.adb.device_list()) == len(
                    self.devices) and len(adbutils.adb.device_list()) > 0:
                out = []
                for connected in adbutils.adb.device_list():
                    out.append(connected.serial)
                outRet = [i for i in self.devices if i not in out]  # 差集
                for offline in outRet:
                    self.pyqtSignal.device.emit(ADBConnectionData(connectionType=ADBConnectionData.TYPE_OUT,
                                                                  connected=
                                                                  None, disConnect=offline, currentDevices=self.devices
                                                                  ))
                    self.devices.remove(offline)
                inRet = [i for i in out if i not in self.devices]
                for online in inRet:
                    self.pyqtSignal.device.emit(ADBConnectionData(connectionType=ADBConnectionData.TYPE_IN,
                                                                  connected=
                                                                  online, disConnect=None, currentDevices=self.devices
                                                                  ))
                    DUtils.socketBroadcast(adbutils.device(online))
                    self.devices.add(online)
                self._notify = True
                continue

        self.pyqtSignal.finished.emit()


class DUtils:

    def __init__(self, device: AdbDevice):
        self.device = device
        self._ERROR_SERVICE_NOT_INSTALL = "Error: Not found; no service started"
        self._ERROR_NOTHING_SERVICE = "(nothing)"
        self.fullData = []

    @staticmethod
    def socketBroadcast(device):
        adbutils.adb.reverse(device.serial, "tcp:9100", "tcp:9100", True)
        agent = DUtils(device)
        agent.sendBroadcast("com.hollyland.action.ADB_CONNECTED")

    @staticmethod
    def waitUntil(function, timeout, period=0.25, *args, **kwargs):
        end = time.time() + timeout
        while time.time() < end:
            if function(args, kwargs):
                return True
            time.sleep(period)
        return False

    def startSocketActivity(self):
        response = self.device.shell([
            'am', 'start', '-n',
            "com.hollyland.hardwaretest" + "/" + ".MainActivity"
        ])
        if "Error" in response:
            return False
        return self.waitUntil(self.isSocketServiceStart, 5)

    def isSocketServiceStart(self):
        cmd = [
            "dumpsys", "activity", "services", "|", "grep",
            ".service.HardwareService"
        ]
        input = self.device.shell(cmd)
        if self._ERROR_NOTHING_SERVICE in input:
            return False
        else:
            return True

    def isServiceInstalled(self):
        """
        服务是否安装
        @rtype: object
        """
        for app in self.device.list_packages():
            if "com.hollyland.hardwaretest" in app:
                return True
        return False

    def startADBSocketService(self):
        """
        开启应服务
        :return:
        """
        try:
            cmd = [
                "am", "startservice", "-n",
                "com.hollyland.hardwaretest/com.hollyland.hardwaretest.service.HardwareService"
            ]
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
            cmd = [
                "am", "stopservice",
                "com.hollyland.hardwaretest/com.hollyland.hardwaretest.service.HardwareService"
            ]
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
        return bytes.fromhex(head) + bytes(SocketMessage.to_json(message),
                                           "utf-8") + bytes.fromhex(tail)

    def socketMessageDecoder(self, response: bytes):
        """
        去除粘包
        :param response:
        :return:
        """
        head = "AA AA AA AA"
        tail = "FF FF FF FF"
        # 不粘包
        if response.startswith(bytes.fromhex(head)) and response.endswith(
                bytes.fromhex(tail)):
            return response.strip(bytes.fromhex(head)).strip(
                bytes.fromhex(tail))
        # 头包
        elif response.startswith(
                bytes.fromhex(head)) and not response.endswith(
            bytes.fromhex(tail)):
            self.fullData.append(response.strip(bytes.fromhex(head)))
            return self.fullData[0]
        # 尾包
        elif response.endswith(
                bytes.fromhex(tail)) and not response.startswith(
            bytes.fromhex(head)):
            self.fullData.append(response.strip(bytes.fromhex(tail)))
            byte_buffer = None
            for buffer in self.fullData:
                byte_buffer += buffer
            self.fullData.clear()
            return byte_buffer
        # 中间包
        elif not response.startswith(
                bytes.fromhex(head)) and not response.endswith(
            bytes.fromhex(tail)):
            if response.decode("utf-8") == "":
                return "null".encode("utf-8")
            self.fullData.append(response)
            byte_buffer = None
            for buffer in self.fullData:
                byte_buffer += buffer
            return byte_buffer

    def forwardByAgentPort(self):
        """_summary_
            forward硬件测试端口
        Returns:
            _type_: _description_
        """
        return self.device.forward("tcp:9100", "tcp:9100")

    def forward2ADBService(self):
        """
        forward 9000端口
        :return:
        """
        return self.device.forward("tcp:9000", "tcp:9000")

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
            logger.info("create connection")
            # 超时
            client.settimeout(10)
            # 握手
            client.send(self.combine(head))
            logger.info("发送消息：{}".format(SocketMessage.to_json(message)))
            logger.info(self.socketMessageDecoder(client.recv(1024)))
            client.send(self.combine(message))
            response = self.socketMessageDecoder(client.recv(1024))
            #print(response)
        except adbutils.errors.AdbError as e:
            return ""
        except TimeoutError as e:
            return "timeout"
        else:
            print("关闭连接")
            client.close()
            return response.decode('utf-8')

    def killPort(self, port):
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

    # adb shell am broadcast -a com.whereismywifeserver.intent.TEST --es sms_body "test from adb"

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



if __name__ == '__main__':

    # 握手
    data = SocketData(version="1.0", type=1, contents=None)
    message = SocketMessage(cmd=3, data=data)

    SNcontents = DetailData("SN", "198911191313", 1)
    btMacContents = DetailData("BT-Mac", "bt:cd:ef:gf:bt", 1)
    wifiMacContents = DetailData("Wi-Fi-Mac", "wf:cd:ef:gf:wf", 1)
    ethMacContents = DetailData("ETH-Mac", "et:cd:ef:gf:et", 1)
    contentslist = []
    contentslist.append(SNcontents)
    contentslist.append(btMacContents)
    contentslist.append(wifiMacContents)
    contentslist.append(ethMacContents)

    writeMacData = SocketData("1.0", 1, contentslist)
    writeMacMessage = SocketMessage(cmd=1, data=writeMacData)

    reportContent = DetailData(name="Image-Result", value="1", dataType=0)
    reportContents = []
    reportContents.append(reportContent)
    reportData = SocketData(version="1.0", type=1, contents=reportContents)
    reportMessage = SocketMessage(cmd=4, data=reportData)

    # 遍历当前连接设备
    for device in adb.device_list():
        if isinstance(device, AdbDevice):
            socket = DUtils(device)
            # string = device.app_start("com.hollyland.production.test", ".MainFactoryActivity")
            # response = device.shell(
            #     ['am', 'start', '-n', "com.hollyland.production.test" + "/" + ".MainFactoryActivity"])
            # print(response)
            # print(socket.isSocketServiceStart())
            socket.forward2ADBService()
            device.forward_list()
            # result = socket.sendBroadcast(
            #     "com.hollyland.action.ADB_CONNECTED")
            # ADB_DISCONNECT
            # print(result)
            device.start_recording("D:\\1.mp4")
            time.sleep(10)
            device.stop_recording()

            # rep = socket.sendMessage(message=message)
            # if rep == "":
            #     print("结束")
            # else:
            #     rep_msg = SocketMessage.from_json(rep)
            #     print(rep_msg)
            #     for contents_name in rep_msg.data.contents:
            #         if contents_name.name == "JPG-File-Path":
            #             print("JPG-File-Path : " + contents_name.value)
            #             device.sync.pull(contents_name.value, "../JPG-File-Path.jpg")
            #         elif contents_name.name == "RAW-File-Path":
            #             print("RAW-File-Path :" + contents_name.value)
            #     socket.sendMessage(writeMacMessage)
            #     socket.sendMessage(reportMessage)
