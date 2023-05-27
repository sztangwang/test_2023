from socket import socket, AF_INET, SOCK_STREAM

from PyQt5.QtCore import *

from config.agentConfig import *


class SocketClient(QThread):

    def __init__(self):
        super().__init__()
        self.isStop = False
        self.address = None
        self.client = None

    def run(self):
        self.client = socket(AF_INET, SOCK_STREAM)
        self.address = (CLIENT_HOST, CLIENT_PORT)
        self.client.connect(self.address)
        while self.isStop:

            pass

    def heartBeatSender(self):
        """
        心跳发送
        """
        pass

    def dataSender(self):
        """
        数据处理
        """
        pass

    def syncSender(self):
        """
        同步处理
        """
        pass

    def stop(self):

        pass