
from PyQt5 import QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QWidget, QToolBar, QAction, QHBoxLayout,QPushButton



class toolLayout(QWidget):
    console_signal = QtCore.pyqtSignal(str, str)

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.select_device = ''
        self.mainwindow = parent
        self.ir_serial = ''
        self.IniUi()

    def IniUi(self):
        self.tool_bar = QToolBar('工具栏')
        # self.adb_combobox = CustomComboBox(self)
        # self.adb_combobox.activated.connect(self.adb_combobox_connect)
        # self.tool_bar.addWidget(self.adb_combobox)
        self.mainwindow.addToolBar(Qt.TopToolBarArea, self.tool_bar)


        self.settings_button = QAction(QIcon(""), "settings", self)
        self.other_button = QAction(QIcon(""), "other", self)

        #self.settings_button.triggered.connect(self.settings_connect)


        self.tool_bar.addActions((self.settings_button,self.other_button))

        layout = QHBoxLayout()
        self.recordMode_button = QPushButton('其他按钮')
        #self.recordMode_button.clicked.connect(self.recordMode_connect)

        layout.addWidget(self.recordMode_button)
        self.widget_spacer = QWidget()
        self.widget_spacer.setLayout(layout)
        self.tool_bar.addWidget(self.widget_spacer)
     
   

    

   


