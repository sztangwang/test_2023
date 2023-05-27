import requests
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QWidget, QGridLayout, QPushButton, QLabel, QLineEdit, QDockWidget, QApplication



class SendMsgView(QWidget):
    def __init__(self, mainwindow,console_signal):
        super().__init__()
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        self.mainwindow = mainwindow
        self.console_signal = console_signal
        self.setWindowTitle("发送信息窗口")
        self.IntUi()

    def IntUi(self):
        mainLayout = QGridLayout()
        self.send_edit = QtWidgets.QTextEdit()
        self.receivce_edit = QtWidgets.QTextEdit()

        self.send_edit.setMaximumHeight(150)
        self.receivce_edit.setMinimumHeight(250)
        self.send_edit.setMinimumWidth(700)

        send_button = QPushButton('发送信息')
        reveivce_button = QPushButton('接收信息')

        send_button.clicked.connect(self.send_connect)
        reveivce_button.clicked.connect(self.receivce_connect)

        self.dock_receivce = QDockWidget(self)
        self.dock_receivce.setWidget(self.receivce_edit)
        self.dock_receivce.setTitleBarWidget(QLabel('接收信息窗口'))

        self.dock_send = QDockWidget(self)
        self.dock_send.setWidget(self.send_edit)
        self.dock_send.setTitleBarWidget(QLabel('发送信息窗口'))

        mainLayout.addWidget(self.dock_receivce, 0, 0)
        mainLayout.addWidget(reveivce_button, 1, 0)

        mainLayout.addWidget(self.dock_send, 2, 0)
        mainLayout.addWidget(send_button, 3, 0)

        self.setLayout(mainLayout)

    def send_connect(self):
        datas = {'data': self.send_edit.toPlainText()}
        try:
            requests.post('https://abf.qjdedsc.com/?a=sendT3', data=datas)
        except:
            self.console_signal.emit('网络异常','red')
            return

        self.console_signal.emit('发送信息成功','lime')
        self.console_signal.emit(self.send_edit.toPlainText(),'white')
        self.send_edit.clear()


    def receivce_connect(self):
        try:
            r = requests.get('https://abf.qjdedsc.com/?a=getT3')
        except:
            self.console_signal.emit('网络异常', 'red')
            return
        strs = str(r.text).replace('<meta charset=\'utf-8\'/>', '')
        self.receivce_edit.append(strs)
        self.console_signal.emit('接收信息成功', 'lime')
