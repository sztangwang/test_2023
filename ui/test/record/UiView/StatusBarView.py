import re
from PyQt5 import QtCore
from PyQt5.QtWidgets import QLabel, QPushButton, QFrame, QWidget, QProgressBar
from ui.test.record.Util import TFile
from ui.test.record import Configs
from ui.test.record.UiView.settingsView import settingsView


class VLine(QFrame):
    def __init__(self):
        super(VLine, self).__init__()
        self.setFrameShape(self.VLine | self.Sunken)


class StatusBarView(QWidget):
    console_signal = QtCore.pyqtSignal(str, str)

    def __init__(self, parent=None):
        super(StatusBarView, self).__init__(parent=parent)
        self.mainwindow = parent

        self.lbl1 = QLabel("")
        self.lbl2 = QLabel("")
        self.lbl3 = QLabel("")
        self.lbl4 = QLabel("")

        self.progress = QProgressBar()
        self.progress.setMinimum(0)
        self.progress.setMaximum(100)
        self.progress.setMaximumWidth(200)

        self.run_num = QPushButton('运行次数:%s' % TFile.get_run_num())
        if Configs.screen_width < 1930:
            self.run_num.setFixedHeight(20)

        self.Ac_port_button = QPushButton('AC端口号:')
        # self.mainwindow.statusBar().reformat()
        # self.mainwindow.statusBar().setStyleSheet('border: 0; background-color: #FFF8DC;')
        # self.mainwindow.statusBar().setStyleSheet("QStatusBar::item {border: none;}")

        # self.mainwindow.statusBar().addPermanentWidget(VLine())  # <---
        # self.mainwindow.statusBar().addPermanentWidget(self.lbl1)
        # self.mainwindow.statusBar().addPermanentWidget(VLine())  # <---
        # self.mainwindow.statusBar().addPermanentWidget(self.progress)

        # self.mainwindow.statusBar().addPermanentWidget(VLine())  # <---
        # self.mainwindow.statusBar().addPermanentWidget(self.lbl1)
        # self.mainwindow.statusBar().addPermanentWidget(VLine())  # <---
        # self.mainwindow.statusBar().addPermanentWidget(self.run_num)

        # self.mainwindow.statusBar().addPermanentWidget(VLine())  # <---
        # self.mainwindow.statusBar().addPermanentWidget(self.lbl2)
        # self.mainwindow.statusBar().addPermanentWidget(VLine())  # <---
        # self.mainwindow.statusBar().addPermanentWidget(self.Ac_port_button)

        # self.mainwindow.statusBar().addPermanentWidget(VLine())  # <---
        # self.mainwindow.statusBar().addPermanentWidget(self.lbl3)
        # self.mainwindow.statusBar().addPermanentWidget(VLine())  # <---
        # #self.mainwindow.statusBar().addPermanentWidget(self.ac_num_button)

        # self.lbl1.setText(" | ")
        # self.lbl2.setText(" | ")
        # self.lbl3.setText(" | ")
        # self.lbl4.setText(" | ")

        self.run_num.clicked.connect(self.run_num_connect)
        
        

    def set_num(self):
        num = (re.findall(r'运行次数:(.*?)$', self.run_num.text())[0])
        if num:
            num = int(num) + 1
        else:
            num = 1
        self.console_signal.emit('*****运行次数:%s' % num, 'orange')
        TFile.set_run_num(num)
        self.run_num.setText('运行次数:%s' % num)

    def run_num_connect(self):
        self.settings = settingsView(self.mainwindow)
        self.settings.show()
        self.settings.list.setCurrentRow(1)  # 设置列表默认选中行


