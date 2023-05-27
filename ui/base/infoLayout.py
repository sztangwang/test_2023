
from PyQt5 import QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QGridLayout, QLabel


class infoLayout(QWidget):
    def __init__(self):
        super(infoLayout, self).__init__()
        self.initUI()

    def initUI(self):
        self.setMaximumWidth(350)

        self.GridLayout = QGridLayout()
        self.GridLayout.addWidget(QLabel('正在执行任务总数量：'), 0, 0,Qt.AlignTop)

        self.setLayout(self.GridLayout)

    def test(self):
        print('test')
 


        
