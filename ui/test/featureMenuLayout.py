from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QFrame, QHBoxLayout, QLabel, QGroupBox, QGridLayout, QListWidget, \
    QPushButton, QDialog, QScrollArea, QHeaderView, QMenu, QMenuBar, QAction, QComboBox, QRadioButton

from utils.fileutils import getResPath


class FeatureMenuLayout(QtWidgets.QWidget):

    def initUI(self, layout: QWidget):
        self.resize(800, 800)
        self.mainLayout = QVBoxLayout()
        layout.setLayout(self.mainLayout)

        # 测试设备选项Frame
        self.deviceFrame = QFrame()
        self.deviceLayout = QHBoxLayout()
        self.deviceFrame.setFrameStyle(QFrame.Box)
        self.deviceFrame.setLayout(self.deviceLayout)

        self.deviceLayout.addWidget(QLabel("设备选择"))
        self.deviceComboBox = QComboBox()
        self.deviceLayout.addWidget(self.deviceComboBox)

        # 测试模式选项Frame
        self.testModelFrame = QFrame()
        self.testModelLayout = QHBoxLayout()
        self.testModelFrame.setFrameStyle(QFrame.Box)
        self.testModelFrame.setLayout(self.testModelLayout)

        self.testModelLayout.addWidget(QLabel("测试模块"))
        self.testModelGbx = QGroupBox()
        self.gbxLayout = QHBoxLayout(self.testModelGbx)

        self.testModelLayout.addWidget(self.testModelGbx)
        self.testModelGbx.layout().addWidget(QRadioButton("软件"))
        self.testModelGbx.layout().addWidget(QRadioButton("硬件"))

        # 测试引擎选项Frame
        self.testEngineFrame = QFrame()
        self.testEngineLayout = QHBoxLayout()
        self.testEngineFrame.setFrameStyle(QFrame.Box)
        self.testEngineLayout.addWidget(QLabel("测试引擎"))
        self.engineLaybel = QLabel("ATX")
        self.testEngineLayout.addWidget(self.engineLaybel)
        self.testEngineFrame.setLayout(self.testEngineLayout)

        # 测试用例选项Frame
        self.testCaseFrame = QFrame()
        self.testCaseLayout = QHBoxLayout()
        self.testCaseFrame.setFrameStyle(QFrame.Box)
        self.testCaseFrame.setLayout(self.testCaseLayout)
        self.testCaseLayout.addWidget(QLabel("测试用例"))



        self.mainLayout.addWidget(self.deviceFrame)
        self.mainLayout.addWidget(self.testModelFrame)
        self.mainLayout.addWidget(self.testEngineFrame)
        self.mainLayout.addWidget(self.testCaseFrame)

        self.mainLayout.setStretch(0, 1)
        self.mainLayout.setStretch(1, 1)
        self.mainLayout.setStretch(2, 1)
        self.mainLayout.setStretch(3, 5)
