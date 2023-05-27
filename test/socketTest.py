import socket
import socketserver
import time
import json
from dataclasses import dataclass
from typing import Optional

from dataclasses_json import dataclass_json
import adbutils
from PyQt5.QtCore import QThread

from common.logger import Logger
from moduel.nettyMessage import *

logger = Logger(level="info").logger
from utils.adbsocket import DUtils


class MyTCPHandler(socketserver.BaseRequestHandler):
    """
    The request handler class for our server.

    It is instantiated once per connection to the server, and must
    override the handle() method to implement communication to the
    client.
    """

    def handle(self):
        # self.request is the TCP socket connected to the client
        # 必须要 while 循环读写才能使得连接不去中断
        while True:
            self.data = self.request.recv(1024).strip()
            print("{} wrote:".format(self.client_address[0]))
            print(self.data)
            # just send back the same data, but upper-cased
            timestamp = int(round(time.time() * 1000))
            nettyMessage = NettyMessage(type=1, timestamp=timestamp, nettyData=None)
            print("send: {}".format(nettyMessage.to_json()))
            self.request.sendall(nettyMessage.to_json().encode("utf-8"))
            time.sleep(5)


@dataclass_json
@dataclass
class Connection:
    socket: object
    sid: int
    deviceId: str


class SocketServer(QThread):

    def __init__(self):
        super().__init__()
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind(("127.0.0.1", 9100))
        self.server.listen(5)
        # 存取链接列表
        self.connection_list = []
        self.isStop = False

    #
    def run(self):
        sid = 0
        logger.info("run")
        while not self.isStop:
            conn, addr = self.server.accept()
            sid = sid + 1
            channel = Connection(conn, sid, "")
            with conn:
                print(f"[CONNECTION] Connected to {addr}")
                while not self.isStop:
                    data = conn.recv(1024)
                    receiverMsg = NettyMessage.from_json(data.decode("utf-8"))
                    if receiverMsg.nettyData.deviceData.deviceSn is not None:
                        channel.deviceId = receiverMsg.nettyData.deviceData.deviceSn
                        self.connection_list.append(channel)
                    print(data)
                    if not data:
                        break
                    resp = self.processor(receiverMsg, sid)
                    conn.sendall(resp.encode("utf-8"))
            print(f"[CONNECTION] Disconnected from {addr}")

    # 数据处理机
    def processor(self, nettyMsg: NettyMessage, sid):
        SYNC_MSG = 0
        HEARTBEAT_MSG = 1
        DATA_MSG = 2

        resp: str
        typeDict = {
            SYNC_MSG: lambda: self.syncMsgProcessor(nettyMsg, sid),
            HEARTBEAT_MSG: lambda: self.heartBeatProcessor(nettyMsg),
            DATA_MSG: lambda: self.dataProcessor(nettyMsg)
        }

        return typeDict[nettyMsg.type]()

    # 信息同步
    def syncMsgProcessor(self, nettyMsg: NettyMessage, sid):
        # 存入sid返回
        nettyMsg.nettyData.deviceData.deviceId = sid
        return nettyMsg.to_json()

    # 心跳处理
    def heartBeatProcessor(self, nettyMsg: NettyMessage):
        nettyMsg.timestamp = int(round(time.time() * 1000))
        return nettyMsg.to_json()

    def dataProcessor(self, nettyMsg: NettyMessage):
        return nettyMsg.to_json()

    def shutDown(self):
        self.isStop = True
        for connection in self.connection_list:
            connection.socket.close()
        self.server.shutdown(socket.SHUT_WR)

if __name__ == '__main__':
    PORT = 9100
    #
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", PORT))
        s.listen(5)
        # print(f"[INFO] Listening on {SERVER}:{PORT}")

        while True:
            conn, addr = s.accept()
            with conn:
                print(f"[CONNECTION] Connected to {addr}")
                while True:
                    data = conn.recv(1024)
                    print(data)
                    if not data:
                        break
                    timestamp = int(round(time.time() * 1000))
                    nettyMessage = NettyMessage(type=1, timestamp=timestamp, nettyData=None)
                    sender = nettyMessage.to_json().encode("utf-8")
                    conn.send(sender)
                    print(f"send {nettyMessage.to_json()}")
            print(f"[CONNECTION] Disconnected from {addr}")
