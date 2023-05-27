from functools import partial

from PyQt5.QtCore import QRunnable, pyqtSlot, QThread, QObject, pyqtSignal
from socket import *
import socketserver
from common.logger import *
from compoment.agentSocketChannel import ChannelThread
from config.agentConfig import *
from moduel.agentConnection import Connection
from moduel.nettyMessage import NettyMessage

logger = Logger(level="info").logger


class ServerSignal(QObject):
    # channel信号到主线程ui信号
    dataTupleSignal = pyqtSignal(tuple)
    # 任务信号到channel信号
    taskMessageSignal = pyqtSignal(tuple)


class SocketServer(QThread):

    def __init__(self, nettyMessage=None, fromTaskSerialsList=None):
        super().__init__()
        # 存取链接列表
        self.nettyMessage = nettyMessage
        self.fromTaskSerialsList = fromTaskSerialsList
        self.server = None
        self.connections = []
        self.serverSignal = ServerSignal()
        self._serviceType = False
        self._isStop = False

    def run(self):
        sid = 0
        self._serviceType = self.isServiceType()
        logger.info("================================Start Holly-land Test Server")
        with socket(AF_INET, SOCK_STREAM) as s:
            self.server = s
            self.server.bind((SERVER_HOST, SERVER_PORT))
            self.server.listen(5)
            while not self._isStop:
                conn, addr = self.server.accept()
                sid = sid + 1
                channel = Connection(conn, sid, "")
                conn.settimeout(60)
                thread = ChannelThread(channel)
                thread.channelSignal.pysignal.connect(self.register)
                thread.channelSignal.finished.connect(self.unregister)
                thread.channelSignal.dataTupleSignal.connect(self.serverSignal.dataTupleSignal)
                thread.channelSignal.taskMessageSignal.connect(self.serverSignal.taskMessageSignal)
                thread.start()

    def stop(self):
        """
        停止线程
        """
        self._isStop = True
        for connection in self.connections: 
            connection.socket.close()
        self.server.shutdown(SHUT_WR)
        self.quit()

    #
    def register(self, channel: Connection):
        """
        注册连接
        @param channel:
        """
        logger.info("register channel")
        self.connections.append(channel)
        for connection in self.connections:
            logger.info(f"SID : {str(connection.sid)} , | deviceID :{channel.deviceId}")
        if self._serviceType:
            self.postChannelTask(channel)

    #
    def unregister(self, sid):
        """
        注销链接
        @param sid:
        """
        for index, connection in enumerate(self.connections):
            if sid == connection.sid:
                removeConnection = self.connections.pop(index)
                logger.info(f"unRegister : SID : {removeConnection.sid} | deviceID :{removeConnection.deviceId}")

    def isServiceType(self):
        """
        是否为GUI模式
        @return:
        """
        if self.nettyMessage is not None and not self.fromTaskSerialsList:
            return True
        return False

    def isStop(self):
        """
        是否为停止状态
        @return:
        """
        return self._isStop

    def postChannelTask(self, channel: Connection):
        """
        执行None-GUI任务
        @param channel:
        @return:
        """
        deviceId = channel.deviceId
        if deviceId is None:
            logger.info(f"Sync deviceId error ... Channel Sid : {channel.sid}")
            return

        if deviceId in self.fromTaskSerialsList:
            self.serverSignal.taskMessageSignal.emit((self.nettyMessage, channel))
