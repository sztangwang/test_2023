import re
import time
from PyQt5 import QtCore
from PyQt5.QtWidgets import (QLabel, QPushButton, QFrame, QWidget, QProgressBar)
from PyQt5.QtCore import QThread,pyqtSignal   # 导入线程模块


class VLine(QFrame):
    def __init__(self):
        super(VLine, self).__init__()
        self.setFrameShape(self.VLine | self.Sunken)


class bottomLayout(QWidget):
    console_signal = QtCore.pyqtSignal(str, str)

    def __init__(self, parent=None):
        super(bottomLayout, self).__init__(parent=parent)
        self.mainwindow = parent

        self.lbl1 = QLabel("")
        self.lbl2 = QLabel("")
        self.lbl3 = QLabel("")
        self.lbl4 = QLabel("")

    
        self.progress = QProgressBar()
        self.progress.setMinimum(0)
        self.progress.setMaximum(100)
        self.progress.setMaximumWidth(200)

        self.connect_server = QPushButton('未连接服务器')
        self.connect_server.setStyleSheet('color: #ef5b9c;')
        self.connect_server.clicked.connect(self.connect_server_clicked)
       
        self.mainwindow.statusBar().reformat()
        self.mainwindow.statusBar().setStyleSheet('border: 0; background-color: #FFF8DC;')
        self.mainwindow.statusBar().setStyleSheet("QStatusBar::item {border: none;}")

        self.mainwindow.statusBar().addPermanentWidget(VLine())  # <---
        self.mainwindow.statusBar().addPermanentWidget(self.lbl1)
        self.mainwindow.statusBar().addPermanentWidget(VLine())  # <---
        self.mainwindow.statusBar().addPermanentWidget(self.progress)

        self.mainwindow.statusBar().addPermanentWidget(VLine())  # <---
        self.mainwindow.statusBar().addPermanentWidget(self.lbl1)
        self.mainwindow.statusBar().addPermanentWidget(VLine())  # <---
        self.mainwindow.statusBar().addPermanentWidget(self.connect_server)

        self.mainwindow.statusBar().addPermanentWidget(VLine())  # <---
        self.mainwindow.statusBar().addPermanentWidget(self.lbl2)
        self.mainwindow.statusBar().addPermanentWidget(VLine())  # <---
        #self.mainwindow.statusBar().addPermanentWidget(self.image_comp_value_button)

        self.mainwindow.statusBar().addPermanentWidget(VLine())  # <---
        self.mainwindow.statusBar().addPermanentWidget(self.lbl3)
        self.mainwindow.statusBar().addPermanentWidget(VLine())  # <---
        #self.mainwindow.statusBar().addPermanentWidget(self.ac_num_button)


        self.lbl1.setText(" | ")
        self.lbl2.setText(" | ")
        self.lbl3.setText(" | ")
        self.lbl4.setText(" | ")


    def connect_server_clicked(self):

        #self.connect_server.setStyleSheet('color: #2EBA9A;')
        self.thread = connect_server_thread(self.connect_server)
        self.thread.set_connect_server_signal.connect(self.set_connect_style)
        self.thread.start()

    def set_connect_style(self, color, text):
        self.connect_server.setStyleSheet(color)
        self.connect_server.setText(text)





class connect_server_thread(QThread): 
    set_connect_server_signal = pyqtSignal(str, str)
    def __init__(self,connect_server,parent=None):
        super(connect_server_thread, self).__init__(parent)
        self.connect_server = connect_server 
      
    
       
    def run(self): 
        self.set_connect_server_signal.emit('color: #fffffb;', '正在连接服务器...')
        time.sleep(5)
        self.set_connect_server_signal.emit('color: #6effe8;', '已连接服务器')
    
        
        





