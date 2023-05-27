from ui.test.record import String
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QWidget, QPushButton, QFormLayout, QComboBox, QCheckBox,QHBoxLayout


class AdbTestView(QWidget):
    def __init__(self, mainwindow):
        super().__init__()
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        self.mainwindow = mainwindow
        self.setWindowTitle(String.Adb_Match)
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


        flayout1.addRow('Adb输入数据:', self.input_content)
        flayout1.addRow('选择Adb匹配类型:', self.match_type)
        flayout1.addRow('检测失败后循环次数:', self.num_edit)
        flayout1.addRow('匹配返回数据:', self.match_content)
        w1 = QWidget()
        w1.setLayout(flayout1)
        w2 = QWidget()
        w2.setLayout(blayout)

        self.add_button = QPushButton("添加"+String.Adb_Match)
        self.add_button.clicked.connect(self.add_connect)
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
        input_text = self.input_content.text()
        types = self.match_type.currentText()
        output_text = '预输出数据' + self.match_content.text()
        if types not in String.Not_Match:
            text = '输入数据%s,%s,%s,失败后循环次数%s' % (input_text, output_text, types,self.num_edit.text())
        else:
            text = '输入数据%s,%s' % (input_text, types)
        buttonItems = [String.Adb_Match, text, '0', '1']
        self.mainwindow.set_signal_select_insert_table_connect(buttonItems)
     
        self.destroy()

    def type_connect(self):
        select = self.match_type.currentText()
        if select not in String.Not_Match:
            self.match_content.setVisible(True)
            self.num_edit.setVisible(True)
        else:
            self.match_content.setVisible(False)
            self.num_edit.setVisible(False)
