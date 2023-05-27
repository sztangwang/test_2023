import os
import subprocess
from PyQt5 import QtCore
from PyQt5.QtCore import Qt
from ui.test.record.Util import TFile
from PyQt5.QtWidgets import QWidget, QListWidget, QGridLayout, QPushButton, QCheckBox, QComboBox, QColorDialog
from PyQt5.QtWidgets import QFormLayout, QLineEdit, QLabel, QStackedWidget



class Camera_QCombox(QComboBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        default_value = TFile.get_config_value("camera_name")
        self.addItem(default_value)
      

    def showPopup(self):
        self.clear()
        CONFIG_PATH = TFile.CONFIG_PATH.replace('\\',"/")
        p = subprocess.Popen(CONFIG_PATH+"/lib/camera.exe", shell=True,  stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        camera_list = str(p.stdout.read(), 'UTF-8').replace('@camera',"").split('\n')  # byte 转 str
        for name in camera_list:
            self.addItem(name)
        super().showPopup()



class settingsView(QWidget):
    def __init__(self, mainwindow):
        super(settingsView, self).__init__()
        self.mainwindow = mainwindow
        self.initUI()

    def initUI(self):
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        self.list = QListWidget()
        self.list.setMinimumWidth(220)
        self.stackWidget = QStackedWidget()
        self.image_settings()  # 图像源设置
        self.run_num_setting()  # 运行次数
        self.ac_setting() # ac设置
 
        # self.wifi_setting()  # wifi测试
        # self.send_string_setting()
        # self.style_setting()  # 风格切换
        # self.notice_setting()  # 通知设置
        # self.crt_setting()  # CRT工具目录设置

        self.tile_bar = QLabel()  # 设置默认第一个标题
        self.tile_bar.setStyleSheet('font-weight: bold')
        ok_button = QPushButton('ok')
        cancel_button = QPushButton('Cancel')
      
        ok_button.clicked.connect(self.ok_connect)
        cancel_button.clicked.connect(self.cancel_connect)

        grid = QGridLayout()
        grid.addWidget(self.list, 0, 0, 0, 2)
        grid.addWidget(self.tile_bar, 0, 2, 1, 2)
        grid.addWidget(self.stackWidget, 1, 2, 1, 2)
        grid.addWidget(ok_button, 2, 2, alignment=Qt.AlignRight)
        grid.addWidget(cancel_button, 2, 3)
        self.setLayout(grid)
        self.list.currentRowChanged.connect(self.stackSwitch)
        self.setWindowTitle("Settings")

        settings_list_select = int(TFile.get_config_value('settings_list_select'))
        self.list.setCurrentRow(settings_list_select)  # 设置列表默认选中行
        self.list.clicked.connect(self.tile_view)

    def tile_view(self):  # 改变标题栏字符
        TFile.set_config_file(self.list.currentIndex().row(), 'settings_list_select')
        self.tile_bar.setText(self.list.currentItem().text())

    def stackSwitch(self, index):  # 选择事件
        self.stackWidget.setCurrentIndex(index)

    def cancel_connect(self):
        self.destroy()

    def ok_connect(self):
        TFile.set_config_file(self.run_loop_num_edit.text(), 'loop_num')
        if self.adb_checkBox.isChecked():
            TFile.set_config_file("adb", 'is_image_view')
        else:
            TFile.set_config_file("card", 'is_image_view')
        TFile.set_config_file(self.power_time_edit.text(),"power_time")    
        TFile.set_config_file(self.card_screen.currentText(),"card_screen")
        self.mainwindow.ToolBarView.run_num.setText('运行次数:' + self.run_num_edit.text())
        TFile.set_run_num(self.run_num_edit.text())
      
        self.destroy()

    def image_settings(self):
        self.list.insertItem(0, '图像源设置')
        widget = QWidget()
        layout = QFormLayout()
        self.card_checkBox = QCheckBox('采集卡')
        self.adb_checkBox = QCheckBox('Adb获取图像')
        self.camera_combobox = Camera_QCombox(self)
        self.camera_combobox.setMinimumWidth(350)
        
        self.card_screen = QComboBox()
        self.card_screen.addItems(["1920x1080","1080x1920"])
        card_screen = TFile.get_config_value("card_screen")
        self.card_screen.addItem(card_screen)

        if TFile.get_config_value('is_image_view') in "adb":
            self.adb_checkBox.setChecked(True)
            # self.adb_checkBox.setStyleSheet("QCheckBox::indicator""{""background-color : #1d953f;""}")
            # self.card_checkBox.setStyleSheet("QCheckBox::indicator""{""background-color : white;""}")
        else:
            # self.adb_checkBox.setStyleSheet("QCheckBox::indicator""{""background-color : white;""}")
            # self.card_checkBox.setStyleSheet("QCheckBox::indicator""{""background-color : #1d953f;""}")
            self.card_checkBox.setChecked(True)

        self.card_checkBox.setTristate(False)
        self.camera_combobox.currentIndexChanged.connect(self.camera_combobox_connect)
        self.card_checkBox.stateChanged.connect(self.swing_card)
        self.adb_checkBox.stateChanged.connect(self.swing_adb)
        
        layout.addRow(self.adb_checkBox)
        layout.addRow(self.card_checkBox)
        layout.addRow('设备：',self.camera_combobox)
        layout.addRow('采集卡分辨率：',self.card_screen)
        widget.setLayout(layout)
        self.stackWidget.addWidget(widget)

    def swing_card(self):
        """采集卡切换复选框事件"""
        if self.card_checkBox.isChecked():
            # self.adb_checkBox.setStyleSheet("QCheckBox::indicator""{""background-color : white;""}")
            # self.card_checkBox.setStyleSheet("QCheckBox::indicator""{""background-color : #1d953f;""}")
            self.adb_checkBox.setChecked(False)
        else:
            # self.card_checkBox.setStyleSheet("QCheckBox::indicator""{""background-color : white;""}")
            # self.adb_checkBox.setStyleSheet("QCheckBox::indicator""{""background-color : #1d953f;""}")
            self.adb_checkBox.setChecked(True)

    def swing_adb(self):
        if self.adb_checkBox.isChecked():
            self.card_checkBox.setChecked(False)
        else:
            self.card_checkBox.setChecked(True)
        

    

    def camera_combobox_connect(self):
        """选择相机名称事件"""
        TFile.set_config_file(self.camera_combobox.currentText().replace('\n','').replace('\r',''),"camera_name")


    def ac_setting(self):
        self.list.insertItem(2, 'AC设置')
        widget = QWidget()
        layout = QFormLayout()
        self.power_time_edit = QLineEdit(TFile.get_config_value('power_time'))
        layout.addRow('power长按时间：',self.power_time_edit)
        widget.setLayout(layout)
        self.stackWidget.addWidget(widget)



    # def ac_setting(self):
    #     self.list.insertItem(2, 'AC 设置')
    #     ac_QWidget = QWidget()
    #     g_layout = QGridLayout()
    #     g_layout.setAlignment(Qt.AlignTop)
    #     ac_com_label = QLabel('AC端口号:')
    #     self.ac_com_edit = QLineEdit()
    #     g_layout.addWidget(ac_com_label, 1, 0)
    #     g_layout.addWidget(self.ac_com_edit, 1, 1, 1, 2)

    #     ac_tips_label = QLabel('如果AC端口不输入默认选择:2303串口名称')
    #     g_layout.addWidget(ac_tips_label, 2, 1, 1, 4)

    #     ac_num_label = QLabel('AC序号：')
    #     g_layout.addWidget(ac_num_label, 3, 0, alignment=Qt.AlignTop)
    #     self.ac_port = locals()
    #     for n in range(1, 9):
    #         self.ac_port[str(n)] = QCheckBox('%s#' % n)
    #         try:
    #             self.ac_port[str(n)].stateChanged.connect(lambda ch, text=n: self.acPort_checkBox_connect(text))
    #         except:
    #             print('创建AC序号异常')
    #         g_layout.addWidget(self.ac_port[str(n)], 3, n, alignment=Qt.AlignTop)
    #     ac_QWidget.setLayout(g_layout)
    #     self.stackWidget.addWidget(ac_QWidget)

    def run_num_setting(self):
        self.list.insertItem(1, '运行次数')
        g_layout = QGridLayout()
        run_num_QWidget = QWidget()
        g_layout.setAlignment(Qt.AlignTop)
       
        self.run_loop_num_edit = QLineEdit(TFile.get_config_value('loop_num'))
        self.run_loop_num_edit.setMaximumWidth(150)
        self.run_loop_num_label = QLabel('运行循环次数:')
        self.run_num_label = QLabel('当前运行次数:')
        self.run_num_edit = QLineEdit(str(TFile.get_run_num()))
        self.run_num_edit.setMaximumWidth(150)
        self.clean_run_num = QPushButton('清零当前运行次数')
        self.clean_run_num.clicked.connect(self.clean_run_num_connect)

        g_layout.addWidget(self.run_loop_num_label, 0, 0)
        g_layout.addWidget(self.run_loop_num_edit, 0, 1, 1, 4)
        g_layout.addWidget(self.run_num_label, 2, 0)
        g_layout.addWidget(self.run_num_edit, 2, 1, Qt.AlignLeft)
        g_layout.addWidget(self.clean_run_num, 3, 0, Qt.AlignLeft)

        run_num_QWidget.setLayout(g_layout)
        self.stackWidget.addWidget(run_num_QWidget)

    def wifi_setting(self):
        self.list.insertItem(4, 'Wi-Fi检测')
        self.wifi_QWidget = QWidget()
        layout = QFormLayout()
        self.wifi_num_edit = QLineEdit()
        self.wifi_num_edit.setMaximumWidth(100)
        layout.addRow('Wi-Fi检测次数:', self.wifi_num_edit)
        self.wifi_QWidget.setLayout(layout)
        self.stackWidget.addWidget(self.wifi_QWidget)

    def send_string_setting(self):
        self.list.insertItem(5, '电脑发送字符串')
        self.send_string_QWidget = QWidget()
        layout = QFormLayout()
        self.string_pre = QCheckBox('发送字符串 “之前” 输入回车')
        self.string_post = QCheckBox('发送字符串 “之后” 输入回车')

        layout.addRow(self.string_pre)
        layout.addRow(self.string_post)
        self.send_string_QWidget.setLayout(layout)
        self.stackWidget.addWidget(self.send_string_QWidget)


    def crt_setting(self):
        self.list.insertItem(8, 'SecureCRT设置')
        self.crt_widget = QWidget()
        layout = QGridLayout()
        layout.setAlignment(Qt.AlignTop)
        log_label = QLabel('CRT Log 存放目录:')
        crt_label = QLabel('CRT 临时文件存放目录:')
        self.crt_log_edit = QLineEdit()
        self.crt_edit = QLineEdit()
        open_log_path = QPushButton('打开文件目录')
        open_crt_path = QPushButton('打开文件目录')

        layout.addWidget(log_label, 0, 0)
        layout.addWidget(self.crt_log_edit, 0, 1)
        layout.addWidget(open_log_path, 0, 2)

        layout.addWidget(crt_label, 1, 0)
        layout.addWidget(self.crt_edit, 1, 1)
        layout.addWidget(open_crt_path, 1, 2)

        open_log_path.clicked.connect(lambda: self.open_file_path_connect(self.crt_log_edit.text()))
        open_crt_path.clicked.connect(lambda: self.open_file_path_connect(self.crt_edit.text()))

        self.crt_widget.setLayout(layout)
        self.stackWidget.addWidget(self.crt_widget)

    def notice_setting(self):
        self.list.insertItem(7, '通知设置')
        self.audio_widget = QWidget()
        layout = QGridLayout()
        layout.setAlignment(Qt.AlignTop)

        self.audio_switch = QCheckBox('是否打开声音预警')

        test = QPushButton('测试')
        open_file_path = QPushButton('打开音频文件存放目录')
        self.alarm_mode = QLineEdit()
        self.audio_select = QComboBox()

        self.qq_switch = QCheckBox('是否打开QQ预警')
        self.qqname = QLineEdit()
        line = QLineEdit()
        line.setMaximumHeight(1)

        test.setMaximumWidth(180)
        self.alarm_mode.setMaximumWidth(180)
        self.audio_select.setMaximumWidth(180)
        open_file_path.setMaximumWidth(180)
        self.qqname.setMaximumWidth(180)

        layout.addWidget(self.audio_switch, 0, 0)
        layout.addWidget(QLabel('选择预警铃声:'), 1, 0)
        layout.addWidget(self.audio_select, 1, 1)
        layout.addWidget(test, 1, 2, Qt.AlignLeft)
        layout.addWidget(open_file_path, 2, 0)
        layout.addWidget(QLabel(''), 3, 0)
        layout.addWidget(line, 4, 0, 1, 3)
        layout.addWidget(self.qq_switch, 5, 0)
        layout.addWidget(QLabel('QQ名称:'), 6, 0)
        layout.addWidget(self.qqname, 6, 1, Qt.AlignLeft)

        open_file_path.clicked.connect(lambda: self.open_file_path_connect('.\\res'))
        self.audio_select.activated.connect(self.regional_image_box_connect)
        test.clicked.connect(self.audio_test_connect)

        self.audio_widget.setLayout(layout)
        self.stackWidget.addWidget(self.audio_widget)

    def open_file_path_connect(self, path):
        try:
            os.startfile(path)
        except:
            print('目录文件错误', path)

    def clean_run_num_connect(self):
        self.mainwindow.ToolBarView.run_num.setText('运行次数:0')
        self.run_num_edit.setText('0')

    def regional_image_box_connect(self):
        select = self.regional_image_box.currentText()
        if select == '对比图静态多少秒预警':
            self.time_edit.setVisible(True)
            self.time_label.setVisible(True)
        else:
            self.time_edit.setVisible(False)
            self.time_label.setVisible(False)

    def setting_background_connect(self):
        col = QColorDialog.getColor()
        if col.isValid():
            self.mainwindow.setStyleSheet('*{background-color: %s}' % col.name())
            self.setStyleSheet('*{background-color: %s}' % col.name())
            self.config_file.qss_edit(col.name(), 'background-color')
            c = col.name().replace('#', '')
            TFile.set_config_file(c, 'background_color')

    def setting_font_color_connect(self):
        col = QColorDialog.getColor()
        if col.isValid():
            self.mainwindow.setStyleSheet('*{color: %s}' % col.name())
            self.setStyleSheet('*{color: %s}' % col.name())
            self.config_file.qss_edit(col.name(), 'color ')
            c = col.name().replace('#', '')
            TFile.set_config_file(c, 'font_color')

    def acPort_checkBox_connect(self, check):
        if self.ac_port[str(check)].isChecked():
            self.ac_port[str(check)].setStyleSheet("color: red;font-size:20px")
        else:
            font_color = TFile.get_config_value('font_color')
            self.ac_port[str(check)].setStyleSheet("color: #%s;font-size:15px" % font_color)

    def twice_comp_checkBox_connect(self):
        if self.twice_comp_checkBox.isChecked():
            self.twice_comp_time_edit.setEnabled(True)
        else:
            self.twice_comp_time_edit.setEnabled(False)


        
