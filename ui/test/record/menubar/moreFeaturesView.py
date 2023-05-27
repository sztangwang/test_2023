import subprocess
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5 import QtCore
from pynput.mouse import Listener
from PyQt5.QtWidgets import QWidget, QAction
from ui.test.record import String
from ui.test.record.Util import TPicture
from ui.test.record.Util import TFile
from ui.test.record.menubar.AdbTestView import AdbTestView
from ui.test.record.menubar.PcSendStringView import PcSendStringView
from ui.test.record.menubar.SerialTestView import SerialTestView
from ui.test.record.menubar.SerialTestView_9805 import SerialTestView_9805
from ui.test.record.menubar.WeditorView import WeditorView


class moreFeaturesView(QWidget):
    console_signal = QtCore.pyqtSignal(str)
    select_insert_table_signal = QtCore.pyqtSignal(list)
    def __init__(self,mainwindow):
        super().__init__()
        self.mainwindow = mainwindow
        self.MoreFeaturesUi()

    def MoreFeaturesUi(self):
        self.MoreFeatures = self.mainwindow.menuBars.addMenu("More")

        self.pc_click_xy = QAction('电脑鼠标点击xy坐标', self)
        self.MoreFeatures.addAction(self.pc_click_xy)
        self.pc_click_xy.triggered.connect(self.pc_click_xy_connect)

        self.pc_screen = QAction('电脑截图图像对比', self)
        self.MoreFeatures.addAction(self.pc_screen)
        self.pc_screen.triggered.connect(self.pc_screen_connect)

        self.adb_test = QAction(String.Adb_Match, self)
        self.MoreFeatures.addAction(self.adb_test)
        self.adb_test.triggered.connect(self.adb_test_connect)
        self.adb_view = AdbTestView(self.mainwindow)

        self.weditor = QAction('uiautomator2录制', self)
        self.MoreFeatures.addAction(self.weditor)
        self.weditor.triggered.connect(self.weditor_connect)

        self.serial_test = QAction(String.serial_test, self)
        self.MoreFeatures.addAction(self.serial_test)
        self.serial_test.triggered.connect(self.serial_test_connect)

        self.serial_test_9805 = QAction("9805串口匹配", self)
        self.MoreFeatures.addAction(self.serial_test_9805)
        self.serial_test_9805.triggered.connect(self.serial_test_9805_connect)

     
      
        self.PcSendStringView = PcSendStringView(self.mainwindow)
        self.SerialTestView = SerialTestView(self.mainwindow)
        self.SerialTestView_9805 = SerialTestView_9805(self.mainwindow)

    def weditor_connect(self):
        try:
            subprocess.Popen(['weditor'])
        except:
            print('未安装weditor库')
            return
        self.WeditorView = WeditorView(self.select_insert_table_signal)
        self.WeditorView.show()

    def serial_test_connect(self):
        self.SerialTestView.show()

    def serial_test_9805_connect(self):
        self.SerialTestView_9805.show()

    def pc_screen_connect(self):
        self.console_signal.emit('进入鼠标点击坐标截图模式')
        with Listener(on_click=self.on_screen) as listener:
            listener.join()

    def pc_send_str_connect(self):
        self.pc_send_string_view.show()

    def pc_click_xy_connect(self):
        self.console_signal.emit('进入鼠标点击坐标录制模式')
       
        with Listener(on_click=self.on_click) as listener:
            listener.join()   

    def on_click(self, x, y, button, pressed):
        if pressed:
            buttonItems = ['电脑鼠标点击xy坐标','无','x%s,y%s'%(x,y), '无','2', '1',String.Exception_List]
            self.select_insert_table_signal.emit(buttonItems)
        return False
    
    def on_screen(self, x, y, button, pressed):
        if pressed:
            self.pc_screen_file = TPicture.get_pc_screen(x,y)
            types = "对比方式:对比一致"
            buttonItems = ['PC截图图像对比',types,'x%s,y%s,对比图:%s'%(x,y,self.pc_screen_file),'10', '2', '1',String.Exception_List]
            self.select_insert_table_signal.emit(buttonItems)
        return False
 

    def adb_test_connect(self):
        self.adb_view.show()

 