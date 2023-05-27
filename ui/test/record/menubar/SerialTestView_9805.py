
import re
from PyQt5 import QtWidgets, QtCore
from serial.tools.list_ports_windows import comports
from PyQt5.QtWidgets import QWidget, QPushButton, QFormLayout, QComboBox, QGridLayout,QHBoxLayout,QLabel
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



class SerialTestView_9805(QWidget):
    def __init__(self, mainwindow):
        super().__init__()
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        self.mainwindow = mainwindow
        self.setWindowTitle("9805串口匹配")
        self.setGeometry(200, 400, 680, 150)
        self.IntUi()

    def IntUi(self):
        flayout = QFormLayout()     # 主布局
        flayout1 = QGridLayout()
        flayout2 = QFormLayout()    # 添加串口事件垂直布局
        blayout = QHBoxLayout()     # 串口水平布局
        self.input_content = QtWidgets.QLineEdit()
        self.match_content = QtWidgets.QLineEdit()
        self.match_type = QComboBox()
        self.serial_box = serial_QCombox(self)

        flayout1.addWidget(QLabel('输入数据:'), 0,0)
        flayout1.addWidget(self.input_content, 0,1,1,3)
        self.local = locals()
        for n in range(1, 6):
            self.local[str(n)] = QLabel('匹配%s' % n)
            self.local[str("match_%s"%n)] = QtWidgets.QLineEdit()
            self.local[str("expect_label%s"%n)] = QLabel('预期值%s' % n)
            self.local[str("expect_%s"%n)] = QtWidgets.QLineEdit()
            self.local[str("differ_label%s"%n)] = QLabel('差值%s' % n)
            self.local[str("differ_%s"%n)] = QtWidgets.QLineEdit()
            flayout1.addWidget(self.local[str(n)],n,0)
            flayout1.addWidget(self.local[str("match_%s"%n)], n,1)
            flayout1.addWidget(self.local[str("expect_label%s"%n)], n,2)
            flayout1.addWidget(self.local[str("expect_%s"%n)], n,3)

            flayout1.addWidget(self.local[str("differ_label%s"%n)], n,4)
            flayout1.addWidget(self.local[str("differ_%s"%n)], n,5)

        flayout1.addWidget(QLabel("选择串口："),8,0)
        flayout1.addWidget(self.serial_box,8,1,1,3)
    
        w1 = QWidget()
        w1.setLayout(flayout1)
        w2 = QWidget()
        w2.setLayout(blayout)

        self.add_button = QPushButton("添加"+String.serial_test)
        self.add_button.clicked.connect(self.add_connect)
        flayout2.addRow(QLabel("偏差：为空，则全字匹配"))
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
        if not input_text:
            self.input_content.setStyleSheet("QLineEdit{background-color: red}")
            return
        text ={}
        for n in range(1, 6):
            text.update({str("match_%s"%n):[self.local[str("match_%s"%n)].text(),
                                            self.local[str("expect_%s"%n)].text(),
                                            self.local[str("differ_%s"%n)].text()]})
            
        text = '%s,匹配数据%s,串口%s' % (input_text,text,self.serial_box.currentText())
        buttonItems = ["9805串口匹配","找到,找不到,不匹配" ,text,self.match_content.text(), '0', '1',String.Exception_List]
        self.mainwindow.set_signal_insert_table_connect(buttonItems)
     
        self.destroy()

    def type_connect(self):
        select = self.match_type.currentText()
        if select not in String.Not_Match:
            self.match_content.setVisible(True)
            self.num_edit.setVisible(True)
        else:
            self.match_content.setVisible(False)
            self.num_edit.setVisible(False)
