

from PyQt5 import QtCore
from ui.test.record.Util import TFile
from PyQt5.QtWidgets import QWidget, QGridLayout, QPushButton, QLabel

class AboutView(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        self.setWindowTitle("About")
    
        screen_width = int(TFile.get_config_value('screen_width'))
        screen_heigth = int(TFile.get_config_value('screen_height'))
        self.setGeometry(screen_width,screen_heigth,500,300)
        self.IntUi()

    def IntUi(self):
        mainLayout = QGridLayout()
        label = QLabel('正在开发中')
        label.setStyleSheet("text-align:Right")
        self.button = QPushButton()
        self.button.setStyleSheet("text-align:left;height:28px")
        mainLayout.addWidget(self.button,0, 0)
        mainLayout.addWidget(label, 1, 0)
        self.setLayout(mainLayout)




