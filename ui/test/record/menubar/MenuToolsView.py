import re
from PyQt5 import QtCore
from PyQt5.QtWidgets import QWidget, QAction, QMessageBox
# from menubar.CommandView import CommandView
# from menubar.SendMsgView import  SendMsgView


class MenuToolsView(QWidget):
    console_signal = QtCore.pyqtSignal(str, str)

    def __init__(self, mainwindow):
        super().__init__()
        self.mainwindow = mainwindow
       
    
        self.ToolsUi()

    def ToolsUi(self):
        self.Tools = self.mainwindow.menuBars.addMenu("  Tools  ")
      
        #self.cameras = QAction('前后置相机切换...', self)
       


        self.dataLog = QAction('打开data Log', self.mainwindow)
        self.macAdds = QAction('串口获取mac地址', self.mainwindow)
        self.crt = QAction('SecureCRT设置', self)

        # self.Tools.addAction(self.crt)
        # self.Tools.addAction(self.sendMsg)
        # self.Tools.addAction(self.command)
        # self.Tools.addAction(self.factory)
        # self.Tools.addAction(self.dog)
        # self.Tools.addAction(self.dataLog)
        # self.Tools.addAction(self.macAdds)


        #self.CommandView = CommandView(self.mainwindow, self.console_signal)
        #self.send_msg = SendMsgView(self.mainwindow, self.console_signal)
       

