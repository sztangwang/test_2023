#!/usr/bin/python
# -*- coding: UTF-8 -*-

import os
import json
from ui.test.Exception_Frame import configs
from ui.test.Exception_Frame import uvc_client
from pathlib import Path
from PyQt5.QtWidgets import *
from PyQt5 import  QtWidgets


class exceptio_frame_ui_main(QtWidgets.QWidget):
    def __init__(self, tuple_device=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.set_ui()
        self.slot_init()
        self.setGeometry(100, 100, 600, 900)


    def set_ui(self):
        self.setWindowTitle('异常帧检测测试')
        self.mm_layout = QVBoxLayout()
        self.l_down_widget = QtWidgets.QWidget()
        self.__layout_main = QtWidgets.QHBoxLayout()
        self.__layout_fun_button = QtWidgets.QGridLayout()
   

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

        self.black_test_checkBox = QCheckBox('黑屏检测')
        self.green_test_checkBox = QCheckBox('绿屏检测')
        self.blurred_screen_test_checkBox = QCheckBox('花屏检测')
   
        self.run_button = QtWidgets.QPushButton(u'开始执行')
       
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

        self.__layout_fun_button.addWidget(self.green_test_checkBox,9,0)
        self.__layout_fun_button.addWidget(self.black_test_checkBox,9,1)
        self.__layout_fun_button.addWidget(self.blurred_screen_test_checkBox,10,0)

        self.green_test_checkBox.setChecked(True)
        self.black_test_checkBox.setChecked(True)
        self.blurred_screen_test_checkBox.setChecked(True)

        self.__layout_fun_button.addWidget(self.run_button,14,0,1,2)
 
        

        self.right_widget_layout = QHBoxLayout()
        self.__layout_main.addLayout(self.__layout_fun_button)
        self.l_down_widget.setLayout(self.__layout_main)
        self.mm_layout.addWidget(self.l_down_widget)
        self.setLayout(self.mm_layout)
      

    def slot_init(self):
        self.run_button.clicked.connect(self.run)
        
    def run(self):
        if self.run_button.text() not in "开始执行":
            self.run_button.setText('开始执行')
            self.run_thread.terminate()
            if self.logcat_thread:
                self.logcat_thread.terminate()
                self.logcat_thread.stop()
            return
        configs.width = int(self.video_width_edit.text())
        configs.height = int(self.video_height_edit.text())
        configs.types = self.video_type_edit.text()
        configs.default_fps = int(self.video_fps_edit.text())
        configs.black_test = self.black_test_checkBox.isChecked()
        configs.green_test = self.green_test_checkBox.isChecked()
        configs.blurred_screen_test = self.blurred_screen_test_checkBox.isChecked()
        configs.run_time = int(self.time_edit.text())

        self.run_thread = uvc_client.Thread()
        self.run_thread.start() 
        self.run_button.setText('停止')
       


    def get_key_code(self,keyword):
        FILE = Path(__file__).resolve()
   
        with open("%s/config.json"%FILE.parents[0], 'r') as fp:
            dict_keys = json.load(fp)
        if keyword in dict_keys.keys():
            return dict_keys[keyword]
        return None

   

    


