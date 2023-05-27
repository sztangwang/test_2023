import time

import threading
from ui.test.record.Util import TFile
from ui.test.record.Util import Remote
from ui.test.record.Util import TAdb 
from ui.test.record import String
from ui.test.record import Configs
from PyQt5.Qt import *
from PyQt5 import QtWidgets, QtCore

class ButtonEventView(QWidget):
    console_signal = QtCore.pyqtSignal(str)
    select_insert_table_signal = QtCore.pyqtSignal(list)

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.mainwindow = parent
        self.IniUi()

    def IniUi(self):
        self.grid = QGridLayout()
        self.set_button()
        self.setLayout(self.grid)
  
        

    def set_button(self):
        buttonList = TFile.get_json_list(TFile.KEY_PATH)
        j = 0
        x = 0
        for i in buttonList:
            button_name = i.split(':')[0]
            self.button = QtWidgets.QPushButton(button_name, self)
            self.button.setText(button_name)
            if Configs.screen_width < 1920:
                self.button.setFixedHeight(20)
            self.button.setFixedHeight(30)
            self.button.clicked.connect(lambda ch, text=button_name: self.button_connect(text))
            self.grid.addWidget(self.button, j, x)
            x = x + 1
            if x % 7 == 0:
                j = j + 1
                x = 0
    def button_connect(self, name):
        t1 = threading.Thread(target=self.button_connect_thread, args=(name,))
        t1.start()
    
    def button_connect_thread(self, name):
        types,content,value,sleep, num ,asserts ="无","无","无",'5', '1',"stop,continue"
        self.console_signal.emit('点击:%s' % name)
       
        if name in String.SCREEN_EXCEPTION_TEST:
            content = "检测黑屏，蓝屏，绿屏"
            
        elif name in String.SCREENSHOT:
            if Configs.IMAGE_SHOW_BUTTON != String.CLOSE_BUTTON:
                return
            file = TFile.get_cache_picture(keyword = "base")
            self.console_signal.emit('%s：%s'%(String.SCREENSHOT,file))
            Configs.is_screenshot = file
            content = "截图保存"

        elif name in String.Image_Comparison:
            if Configs.IMAGE_SHOW_BUTTON != String.CLOSE_BUTTON:
                return
            file = TFile.get_cache_picture(keyword = "base")
            self.console_signal.emit('%s：%s'%(String.SCREENSHOT,file))
            Configs.is_screenshot = file
            types = String.comparison_type
            value = "10"
            content = file
           
        elif name in String.Ac_On:
            Remote.ac_on()
               
        elif name in String.Ac_Off:
            Remote.ac_off()
               
        elif name in String.Usb_On:
            Remote.usb_on()
                
        elif name in String.Usb_Off:
            Remote.usb_off()
                
        elif name in String.Power:
            Remote.power()
               

        elif name in String.OneKey_Power:
            if not Remote.ac_off():
                self.console_signal.emit(String.Serial_Exception)
            time.sleep(4)
            if not Remote.ac_on():
                self.console_signal.emit(String.Serial_Exception)
            time.sleep(2)
            if not Remote.power():
                self.console_signal.emit(String.Serial_Exception)

        elif name in String.Adb_activity:
            value = TAdb.app_current_match(activity='acitivity')
            types = String.find_type
            self.console_signal.emit('activity=%s'%value)
            
        elif name in String.Adb_package:
            value = TAdb.app_current_match(package='package')
            types = String.find_type
            self.console_signal.emit('package=%s'%value)

        elif name in String.Adb_App_start:
            value = str(TAdb.app_current_match()).replace('RunningAppInfo(','')
            types = String.find_type
            self.console_signal.emit(str(value))
           
        else:
            if not TAdb.send_key(name):
                self.console_signal.emit('未选择设备')
                return
            content = name
            name = String.Adb_Send_Key

        #self.mainwindow.status_bar_view.Ac_port_button.setText('AC端口号:%s'%Configs.ac_port)
    
        if self.mainwindow.ToolBarView.recordMode_button.text() == String.Turn_On_Record_Mode:
            return
        buttonItems = [name,types,content,value, sleep, num,asserts]
        self.select_insert_table_signal.emit(buttonItems)


    
class MoreButtonView(QWidget):
    moreButton_signal = QtCore.pyqtSignal(str)
    def __init__(self, mainwindow):
        super().__init__()
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        self.mainwindow = mainwindow
        self.setWindowTitle("更多按钮")
        self.IntUi()

    def IntUi(self):
        self.grid = QGridLayout()
        self.setLayout(self.grid)
        buttonList =TFile.get_key_list('%s/res/key/morebutton'%TFile.FILE.parents[1])
        j = 0
        x = 0
        for i in buttonList:
            button_name = i.split(':')[0]
            self.button = QtWidgets.QPushButton(button_name, self)
            self.button.setText(button_name)
            self.button.setFixedHeight(30)
            if button_name.isdigit():self.button.setStyleSheet('background-color:orange;color:white')
            self.button.clicked.connect(lambda ch, text=button_name: self.button_connect(text))
            self.grid.addWidget(self.button, j, x)
            x = x + 1
            if x % 6 == 0:
                j = j + 1
                x = 0
    def button_connect(self,text):
        self.moreButton_signal.emit(text)

    def closeEvent(self, event):
        self.destroy()

