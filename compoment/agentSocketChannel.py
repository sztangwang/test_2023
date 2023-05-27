import time

from PyQt5.QtCore import pyqtSignal, QThread, pyqtSlot, QObject, QRunnable

from moduel.agentConnection import Connection
from moduel.nettyMessage import NettyMessage

from common.logger import *

logger = Logger(level="info").logger


class ChannelSignal(QObject):
    pysignal = pyqtSignal(Connection)   # 连接信号

    dataSignal = pyqtSignal(str)         # 数据信号

    finished = pyqtSignal(int)           # 发送完成信号

    dataTupleSignal = pyqtSignal(tuple)   # 给某个管道发送信号

    taskMessageSignal = pyqtSignal(tuple)  # 任务消息信号


# 管道链接类
class ChannelThread(QThread):

    def __init__(self, channel: Connection):
        super().__init__()
        self.channel = channel
        self.isStop = False
        self.channelSignal = ChannelSignal()
        self.channelSignal.taskMessageSignal.connect(self.taskProcessor)

    def run(self):
        with self.channel.socket:
            while not self.isStop:
                data = self.channel.socket.recv(1024).decode("utf-8")
                #logger.info(f"receive Data {data} | SID : {self.channel.sid} | deviceID : {self.channel.deviceId}")
                if not data:
                    logger.info(f"Channel exit!!! | {self.channel.sid} | deviceID : {self.channel.deviceId}")
                    self.channelSignal.finished.emit(self.channel.sid)
                    break
                receiverMsg = NettyMessage.from_json(data)
                resp = self.processor(receiverMsg, self.channel).encode("utf-8")
                #logger.info(f"send Data {resp} | SID : {self.channel.sid} | deviceID : {self.channel.deviceId}")
                self.channel.socket.sendall(resp)

    def processor(self, nettyMsg: NettyMessage, channel: Connection):
        SYNC_MSG = 0
        HEARTBEAT_MSG = 1
        DATA_MSG = 2

        resp: str
        typeDict = {
            SYNC_MSG: lambda: self.syncMsgProcessor(nettyMsg, channel),
            HEARTBEAT_MSG: lambda: self.heartBeatProcessor(nettyMsg, channel),
            DATA_MSG: lambda: self.dataProcessor(nettyMsg, channel)
        }

        return typeDict[nettyMsg.type]()

    # 信息同步

    def syncMsgProcessor(self, nettyMsg: NettyMessage, channel: Connection):
        # 存入sid返回
        if nettyMsg.nettyData.deviceData.deviceSn is not None:
            channel.deviceId = nettyMsg.nettyData.deviceData.deviceSn
            self.channelSignal.pysignal.emit(channel)
            self.channelSignal.dataTupleSignal.emit((nettyMsg, channel))
        nettyMsg.nettyData.deviceData.deviceId = channel.sid
        # 同步sid
        return nettyMsg.to_json()

    # 心跳处理
    def heartBeatProcessor(self, nettyMsg: NettyMessage, channel: Connection):
        self.channelSignal.dataTupleSignal.emit((nettyMsg, channel))
        nettyMsg.timestamp = int(round(time.time() * 1000))
        return nettyMsg.to_json()

    # 数据处理机
    def dataProcessor(self, nettyMsg: NettyMessage, channel: Connection):
        self.channelSignal.dataTupleSignal.emit((nettyMsg, channel))
        return nettyMsg.to_json()

    # 任务处理
    def taskProcessor(self, request: tuple):
        nettyMessage, channel = request
        if channel.sid == self.channel.sid:
            self.channel.socket.sendall(nettyMessage.to_json().encode("utf-8"))
            response = self.channel.socket.recv(1024).decode("utf-8")
            self.channelSignal.dataTupleSignal.emit((NettyMessage.from_json(response), channel))

    def stop(self):
        self.isStop = True


# 单个Channel收发
class ChannelSingle(QRunnable):

    def __init__(self, channel: Connection, request: str):
        super().__init__()
        self.channel = channel
        self.request = request
        self.signal = ChannelSignal()

    def run(self):
        self.channel.socket.sendall(self.request.encode("utf-8"))
        self.signal.dataSignal.emit(self.channel.socket.recv(1024).decode("utf-8"))
