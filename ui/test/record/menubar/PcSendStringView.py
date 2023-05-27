from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QGridLayout, QPushButton, QLabel, QDockWidget



class PcSendStringView(QWidget):
    def __init__(self,mainwindow):
        super().__init__()
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        self.mainwindow = mainwindow
        self.setWindowTitle("添加电脑发送字符串事件")
        self.setGeometry(200, 40, 380, 150)
        self.IntUi()

    def IntUi(self):
        mainLayout = QGridLayout()

        ok_button = QPushButton('OK')
        cancel_button = QPushButton('Cancel')

        self.string_edit = QtWidgets.QTextEdit('')

        self.dock_mainLayout = QDockWidget(self)
        self.dock_mainLayout.setWidget(self.string_edit)
        self.dock_mainLayout.setTitleBarWidget(QLabel('电脑发送字符串:'))

        mainLayout.addWidget(self.dock_mainLayout, 0, 0, 0, 2, alignment=Qt.AlignTop)
        mainLayout.addWidget(ok_button, 1, 0)
        mainLayout.addWidget(cancel_button, 1, 1)

        cancel_button.clicked.connect(self.cancel_connect)
        ok_button.clicked.connect(self.ok_connect)

        self.setLayout(mainLayout)

    def cancel_connect(self):
        self.destroy()

    def ok_connect(self):
        text = self.string_edit.toPlainText()
        if text:
            buttonItems = ['电脑发送字符串', text, '0', '1']
            writeTable().select_table(self.mainwindow, buttonItems)
            self.destroy()
