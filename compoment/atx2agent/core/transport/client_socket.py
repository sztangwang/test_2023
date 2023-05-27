
import socket
import time
from enum import Enum

from compoment.atx2agent.core.common.logs.log_uru import Logger

logger = Logger().get_logger
class StepType(Enum):
    """
    步骤日志类型
    """
    INFO = 1
    PASS = 2
    WARN = 3
    ERROR = 4

class DeviceStatus(Enum):
    """
    设备状态
    """
    ONLINE = 0
    OFFLINE = 1
    TESTING = 2
    DEBUGGING = 3
    ERROR = 4
    UNAUTHORIZED = 5
    DISCONNECTED = 6


class ConditionEnum(Enum):
    """
    执行条件类型
    """
    NONE = 0
    IF = 1
    ELSE_IF = 2
    ELSE = 3
    WHILE = 4
    FOR = 5


class RunLogUtil:
    def __init__(self):
        self.caseId = ""
        self.resultId = ""
        self.status = ""
        self.udid = ""

    def send_to_server(self, msg):
        """
        发送数据到服务器端
        :return:
        """
        msg.update({"caseId": self.caseId, "resultId": self.resultId, "status": self.status, "udid": self.udid})
        msg.update({"time：":time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())})

        ClientSocket("192.168.0.4",9000).send(msg)
        logger.info("发送数据到服务器端：{}".format(msg))

    def send_step(self, status,des,detail):
        """
        发送数据到服务器端
        :return:
        """
        msg= dict
        msg.update({"msg": "step", "des": des, "status": status, "log": detail})
        self.send_to_server(msg)

    def send_test_status(self, status):
        """
        发送测试状态到服务器端
        :return:
        """
        msg= dict
        msg.update({"msg": "status", "des": "", "status": status, "log": ""})
        self.send_to_server(msg)

    def send_android_info(self,platform,version,udid,manufacturer,model,api,size):
        """
        发送测试状态到服务器端
        :return:
        """
        self.send_step(StepType.INFO, "",
                    "设备操作系统：" + platform
                    + "<br>操作系统版本：" + version
                    + "<br>设备序列号：" + udid
                    + "<br>设备制造商：" + manufacturer
                    + "<br>设备型号：" + model
                    + "<br>安卓API等级：" + api
                    + "<br>设备分辨率：" + size
                    )

class ClientSocket:
    """
     连接服务器的socket
    """
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.socket = None

    def connect(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.host, self.port))

    def send(self, data):
        self.socket.send(data)

    def recv(self, size):
        return self.socket.recv(size)

    def close(self):
        self.socket.close()
class TransportWorker:
    def send(self, data):
        pass