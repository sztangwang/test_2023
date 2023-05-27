import re
import time
import threading
from PyQt5 import QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from ui.test.record.Util import TFile
from ui.test.record import Configs
from ui.test.record import String
from  ui.test.record.UiView.settingsView import settingsView
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QAbstractItemView,QPushButton
from  ui.test.record.Util import TAdb 
from PyQt5.QtWidgets import QComboBox
from PyQt5.QtWidgets import QHBoxLayout, QLabel, QComboBox, QPushButton

class CustomComboBox(QComboBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.Devicelist = TAdb.get_device_ip_dict()
        default_value = TFile.get_config_value("CurrentDevice")
        if default_value in self.Devicelist:
            TAdb._device_name = default_value
            self.addItem(default_value)
        else:
            self.addItem('请选择设备号')
            TFile.set_config_file('', "CurrentDevice") # 如果不存在则将config文件清空


    
    def showPopup(self):
        self.clear()
        self.addItem('请选择设备号 ')
        self.Devicelist = TAdb.get_device_ip_dict()
        if not self.Devicelist:
            print("无设备，需要刷新")
            return
        for device in self.Devicelist:
            TAdb._device_name = device
            self.addItem(device)
            super().showPopup()



class ToolBarView(QWidget):
    console_signal = QtCore.pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.mainwindow = parent
        self.select_device = ''
        self.background_color = TFile.get_config_value('background_color')
        self.IniUi()
      
     

    def IniUi(self):
        self.toolbar_layout = QHBoxLayout()
        self.adb_combobox = CustomComboBox(self)
        self.adb_combobox.setMinimumWidth(250)
        self.renovate_button = QPushButton()
        self.run_button = QPushButton()
        self.settings_button = QPushButton()
        self.recordMode_button = QPushButton('开启录制模式')
        self.run_num = QPushButton('运行次数:%s' % TFile.get_run_num())
        self.run_button.setObjectName("Run")

        self.label = QLabel(" ")

        self.renovate_button.setIcon(QIcon("%s刷新.png"%TFile.get_scrcpy_icons_path()))
        self.run_button.setIcon(QIcon("%s运行.png"%TFile.get_scrcpy_icons_path()))
        self.settings_button.setIcon(QIcon("%s设置.png"%TFile.get_scrcpy_icons_path()))

        self.renovate_button.setFixedSize(35,35)
        self.run_button.setFixedSize(35,35)
        self.settings_button.setFixedSize(35,35)
        self.label.setMinimumWidth(800)

        self.adb_combobox.activated.connect(self.adb_combobox_connect)
        self.recordMode_button.clicked.connect(self.recordMode_connect)
        self.settings_button.clicked.connect(self.settings_connect)
        self.run_button.clicked.connect(self.run_connect)
        self.run_num.clicked.connect(self.run_num_connect)
    
        self.toolbar_layout.addWidget(self.adb_combobox, 0, Qt.AlignLeft | Qt.AlignTop)
        self.toolbar_layout.addWidget(self.renovate_button, 0, Qt.AlignLeft | Qt.AlignTop)
        self.toolbar_layout.addWidget(self.settings_button, 0, Qt.AlignLeft | Qt.AlignTop)
        self.toolbar_layout.addWidget(self.run_button, 0, Qt.AlignLeft | Qt.AlignTop)
        self.toolbar_layout.addWidget(self.recordMode_button, 0, Qt.AlignLeft | Qt.AlignTop)
        self.toolbar_layout.addWidget(self.run_num, 0, Qt.AlignLeft | Qt.AlignTop)
        self.toolbar_layout.addWidget(self.label, 0, Qt.AlignRight)
        self.toolbar_layout.setSpacing(10)

        self.setLayout(self.toolbar_layout)
        
        self.settings = settingsView(self.mainwindow)


    def recordMode_connect(self):
        self.console_signal.emit(self.sender().text())
        if self.recordMode_button.text() == '开启录制模式':
            self.recordMode_button.setText('关闭录制模式')
        else:
            self.recordMode_button.setText('开启录制模式')

    def set_num(self):
        num = (re.findall(r'运行次数:(.*?)$', self.run_num.text())[0])
        if num:
            num = int(num) + 1
        else:
            num = 1
        self.console_signal.emit('*****运行次数:%s' % num)
        TFile.set_run_num(num)
        self.run_num.setText('运行次数:%s' % num)

    def adb_combobox_connect(self):
        thread = threading.Thread(target=self.adb_connect_thread)
        thread.start()

    def run_num_connect(self):
        self.settings = settingsView(self.mainwindow)
        self.settings.show()
        self.settings.list.setCurrentRow(1)  # 设置列表默认选中行

        
    def adb_connect_thread(self):
        self.select_device = self.adb_combobox.currentText()  # 获取选择项
        TFile.set_config_file(self.select_device, "CurrentDevice") 
        if not self.select_device:
            return
        if self.select_device.count('.') < 2:  # 如果是ip则启动tcpip命令
            TAdb.start_tcpip(self.select_device)
        else:
            out = TAdb.adb_connect(self.select_device)
            if out.count('拒绝') > 0:
                self.console_signal.emit(out)
                return
            TAdb._device_name = self.select_device
            self.console_signal.emit(out)
        self.console_signal.emit('已连接设备：'+self.select_device)


        
       
    def renovate_connect(self):
        thread = threading.Thread(target=self.renovate_thread)
        thread.setDaemon(True)  
        thread.start()

    def renovate_thread(self):
         self.device_dict = TAdb.get_device_ip_dict()
         for device in self.device_dict:
            self.adb_combobox.addItem(self.device_dict.get(device))
         self.adb_combobox.addItem(device)
         Configs.device_dict = self.device_dict
   

    def run_connect(self):
        self.mainwindow.FileTreeView.setSelectionMode(QAbstractItemView.NoSelection)  # 设置不可选择脚本文件
        self.console_signal.emit('手动点击:%s' % self.run_button.objectName())
        if self.run_button.objectName() == 'Run':
            self.recordMode_button.setText('开启录制模式')
            self.run_button.setIcon(QIcon("%s停止.png"%TFile.get_scrcpy_icons_path()))
            self.mainwindow.run_thread.run_thread_is_on = True
            self.mainwindow.run_thread.start()
            self.run_button.setObjectName("Stop")
        else:
            self.run_stop()

    def run_stop(self):
        self.run_button.setObjectName("Run")
        self.mainwindow.run_thread.run_thread_is_on = False
        self.mainwindow.run_thread.terminate()
        self.mainwindow.run_thread.quit()
        self.console_signal.emit('关闭测试')
        self.mainwindow.FileTreeView.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.run_button.setIcon(QIcon("%s运行.png"%TFile.get_scrcpy_icons_path()))



    def settings_connect(self):
        self.settings.show()




