from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QWidget, QGridLayout, QPushButton, QLabel, QDockWidget

class voiceTestView(QWidget):
    def __init__(self, mainwindow):
        super().__init__()
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        self.mainwindow = mainwindow
        self.setWindowTitle("语音测试")
        self.IntUi()

    def IntUi(self):
        mainLayout = QGridLayout()
        add_voice_button = QPushButton('添加语音事件')
        test_button = QPushButton('测试')
        cancel_button = QPushButton('Cancel')
        self.voice_edit = QtWidgets.QTextEdit()

        cancel_button.clicked.connect(self.cancel_connect)
        add_voice_button.clicked.connect(self.add_voice_connect)
        test_button.clicked.connect(self.test_connect)


        self.dock_mainLayout = QDockWidget(self)
        self.dock_mainLayout.setWidget(self.voice_edit)
        self.dock_mainLayout.setTitleBarWidget(QLabel('请输入语音字符:'))


        mainLayout.addWidget(self.dock_mainLayout, 0, 1,0,3)
        mainLayout.addWidget(add_voice_button, 1, 0)
        mainLayout.addWidget(test_button, 0, 0)
        mainLayout.addWidget(cancel_button, 2, 0)
        self.setLayout(mainLayout)


    def cancel_connect(self):
        self.destroy()

    def add_voice_connect(self):
        if self.voice_edit.toPlainText() != '':
            voiceTts(self.voice_edit.toPlainText(), 90, self.mainwindow).run()
            buttonItems = ['语音测试', self.voice_edit.toPlainText(), '5', '1']
            writeTable().select_table(self.mainwindow, buttonItems)
            self.destroy()

    def test_connect(self):
        voiceTts(self.voice_edit.toPlainText(), 90, self.mainwindow).run()




