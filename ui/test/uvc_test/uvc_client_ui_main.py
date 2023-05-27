#!/usr/bin/python
# -*- coding: UTF-8 -*-

import os
import json
from ui.test.uvc_test import uvc_client
from ui.test.uvc_test import Logcat
from pathlib import Path
from PyQt5.QtWidgets import *
from PyQt5 import  QtWidgets
from adbutils import AdbDevice, adb


class uvc_client_ui_main(QtWidgets.QWidget):
    def __init__(self, tuple_device=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.set_ui()
        self.slot_init()
        self.setGeometry(100, 100, 600, 900)


    def set_ui(self):
        self.setWindowTitle('uvc帧检测测试')
        self.mm_layout = QVBoxLayout()
        self.l_down_widget = QtWidgets.QWidget()
        self.__layout_main = QtWidgets.QHBoxLayout()
        self.__layout_fun_button = QtWidgets.QGridLayout()
   
        self.button_open_camera = QtWidgets.QPushButton(u'打开相机')
        self.button_cap = QtWidgets.QPushButton(u'拍照')

        self.video_type_label = QLabel('视频格式:')
        self.video_type_edit = QLineEdit(self.get_key_code('video_type'))
        
        self.video_width_label = QLabel('视频宽度:')
        self.video_width_edit = QLineEdit(self.get_key_code('video_width'))

        self.video_height_label = QLabel('视频高度:')
        self.video_height_edit = QLineEdit(self.get_key_code('video_height'))

        self.video_fps_label = QLabel('视频帧率:')
        self.video_fps_edit = QLineEdit(self.get_key_code('video_fps'))

        self.num_label = QLabel('执行次数:')
        self.num_edit = QLineEdit(self.get_key_code('num'))

        self.time_label = QLabel('执行时间(s):')
        self.time_edit = QLineEdit(self.get_key_code('time'))

        self.period_label = QLabel('每帧的间隔周期:')
        self.period_edit = QLineEdit(self.get_key_code('period'))

        self.open_or_close_time_label = QLabel('每次打开/关闭uvc的间隔时间:')
        self.open_or_close_time_edit = QLineEdit(self.get_key_code('open_or_close_time'))

        self.run_type_label = QLabel('执行动作:')
        
        self.run_type1 = QComboBox()
        self.run_type1.addItems(['1:执行帧率稳定性检测',"2:执行打开关闭操作","3:执行定屏检测,执行1和3的时候不需要设置执行次数和sleep时间"])
    
        self.logcat_box = QComboBox()
        self.logcat_box.addItems(self.get_ip_list())

        # self.logcat_box.addItems(['1:执行帧率稳定性检测',"2:执行打开关闭操作","3:执行定屏检测,执行1和3的时候不需要设置执行次数和sleep时间"])
    
        self.run_button = QtWidgets.QPushButton(u'开始执行')
        self.Log_label = QLabel("LogPATH:当前目录下csv文件")
       

        self.__layout_fun_button.addWidget(self.video_type_label,2,0)
        self.__layout_fun_button.addWidget(self.video_type_edit,2,1)

        self.__layout_fun_button.addWidget(self.video_width_label,3,0)
        self.__layout_fun_button.addWidget(self.video_width_edit,3,1)

        self.__layout_fun_button.addWidget(self.video_height_label,4,0)
        self.__layout_fun_button.addWidget(self.video_height_edit,4,1)

        self.__layout_fun_button.addWidget(self.video_fps_label,5,0)
        self.__layout_fun_button.addWidget(self.video_fps_edit,5,1)

        self.__layout_fun_button.addWidget(self.num_label,6,0)
        self.__layout_fun_button.addWidget(self.num_edit,6,1)

        self.__layout_fun_button.addWidget(self.time_label,7,0)
        self.__layout_fun_button.addWidget(self.time_edit,7,1)

        self.__layout_fun_button.addWidget(self.period_label,8,0)
        self.__layout_fun_button.addWidget(self.period_edit,8,1)

        self.__layout_fun_button.addWidget(self.open_or_close_time_label,9,0)
        self.__layout_fun_button.addWidget(self.open_or_close_time_edit,9,1)

        self.__layout_fun_button.addWidget(self.run_type_label,10,0)
        self.__layout_fun_button.addWidget(self.run_type1,11,0,1,2)

        self.__layout_fun_button.addWidget(self.logcat_box,12,0)
        self.__layout_fun_button.addWidget(self.run_button,14,0)
        self.__layout_fun_button.addWidget(self.Log_label,14,1)
        

        self.right_widget_layout = QHBoxLayout()
        self.__layout_main.addLayout(self.__layout_fun_button)
        self.l_down_widget.setLayout(self.__layout_main)
        self.mm_layout.addWidget(self.l_down_widget)
        self.setLayout(self.mm_layout)
        self.logcat_thread = None

    

    def slot_init(self):
        self.run_button.clicked.connect(self.run)

    
    def run(self):
        if self.run_button.text() not in "开始执行":
            self.run_button.setText('开始执行')
            self.run_thread.terminate()
            if self.logcat_thread:
                self.logcat_thread.terminate()
                self.logcat_thread.stop()

            #self.run_thread.stop()
            return
        self.run_thread = uvc_client.Thread(self.video_type_edit.text(),int(self.video_width_edit.text()),
                       int(self.video_height_edit.text()),int(self.video_fps_edit.text()),
                       int(self.num_edit.text()),int(self.period_edit.text()),
                       int(self.open_or_close_time_edit.text()),self.run_type1.currentText()[0],
                       int(self.time_edit.text()))
        self.run_thread.start() 
        
        self.run_button.setText('停止')
       

        if self.logcat_box.currentText()[0] not in "请选择网络adb服务":
            self.logcat_thread = Logcat.Thread(self.logcat_box.currentText())
            self.logcat_thread.start()

     
    def get_key_code(self,keyword):
        FILE = Path(__file__).resolve()
   
        with open("%s/config.json"%FILE.parents[0], 'r') as fp:
            dict_keys = json.load(fp)
        if keyword in dict_keys.keys():
            return dict_keys[keyword]
        return None
    
    def get_ip_list(self):
        device_list = ['请选择网络adb服务']
        devices = self.get_device_list()
        device_list = devices + device_list
    
        return device_list
   

    
    def get_device_list(self):
        devices = []
        for device in adb.device_list():
            if isinstance(device, AdbDevice):
                if device.serial not in devices:
                    devices.append(device.serial)
                    #print("接入设备：{}".format(device.serial))
        return devices



    # def closeEvent(self, event):
    #     event.accept()
    #     os._exit(0)


