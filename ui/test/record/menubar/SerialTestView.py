
import re
from PyQt5 import QtWidgets, QtCore
from serial.tools.list_ports_windows import comports
from PyQt5.QtWidgets import QWidget, QPushButton, QFormLayout, QComboBox, QLabel,QHBoxLayout
from ui.test.record import String

class serial_QCombox(QComboBox):
    def __init__(self, parent=None):
        super().__init__(parent)


    def showPopup(self):
        self.clear()
        port_list = list(comports())
        print(port_list)
      
        for port in port_list:
            port = (re.findall(r"COM(.+?) ", str(port))[0])
            self.addItem(str(port))

        super().showPopup()



class SerialTestView(QWidget):
    def __init__(self, mainwindow):
        super().__init__()
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        self.mainwindow = mainwindow
        self.setWindowTitle(String.serial_test)
        self.setGeometry(200, 400, 680, 150)
        self.IntUi()

    def IntUi(self):
        flayout = QFormLayout()     # 主布局
        flayout1 = QFormLayout()
        flayout2 = QFormLayout()    # 添加串口事件垂直布局
        blayout = QHBoxLayout()     # 串口水平布局
        self.num_edit = QtWidgets.QLineEdit('1')
        self.input_content = QtWidgets.QLineEdit()
        self.match_content = QtWidgets.QLineEdit()
        self.match_type = QComboBox()
        self.serial_box = serial_QCombox(self)


        flayout1.addRow('串口写入数据:', self.input_content)
        flayout1.addRow('匹配类型:', self.match_type)
        flayout1.addRow('检测失败后循环次数:', self.num_edit)
        flayout1.addRow('匹配返回数据:', self.match_content)
        flayout1.addRow('选择串口:', self.serial_box)

        w1 = QWidget()
        w1.setLayout(flayout1)
        w2 = QWidget()
        w2.setLayout(blayout)

        self.add_button = QPushButton("添加"+String.serial_test)
        self.add_button.clicked.connect(self.add_connect)
        
        flayout2.addRow(QLabel("串口写入数据：为空，则不写入只匹配"))
        flayout2.addRow(QLabel("匹配返回数据：为空，则不匹配只写入"))
        flayout2.addRow(self.add_button)
        w3 = QWidget()
        w3.setLayout(flayout2)

        self.match_type.addItems([String.Find, String.Not_Find, String.Not_Match])
        self.match_type.activated.connect(self.type_connect)
        self.add_button.setMinimumHeight(35)

        flayout.addWidget(w1)
        flayout.addWidget(w2)
        flayout.addWidget(w3)
       
        self.setLayout(flayout)


    def cancel_connect(self):
        self.destroy()

    def add_connect(self):
        if not self.serial_box.currentText():
            self.serial_box.setStyleSheet("QComboBox{background-color: red}")
            return
        
        input_text = self.input_content.text()
        if input_text:
            input_text = "输入数据%s,"%input_text
        text = '%s串口%s' % (input_text,self.serial_box.currentText())
        
        buttonItems = [String.serial_test,"找到,找不到,不匹配" ,text,self.match_content.text(), '0', '1',String.Exception_List]
        self.mainwindow.set_signal_insert_table_connect(buttonItems)
     
        self.destroy()

    def type_connect(self):
        if self.match_type.currentText() not in String.Not_Match:
            self.match_content.setVisible(True)
            self.num_edit.setVisible(True)
        else:
            self.match_content.setVisible(False)
            self.num_edit.setVisible(False)
