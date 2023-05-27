

import requests
from Util import TFile
from PyQt5 import QtCore
from PyQt5.QtCore import QThread
from PyQt5.QtWidgets import QWidget, QGridLayout, QPushButton, QLabel


class CommandView(QWidget):
    def __init__(self, mainwindow, console_signal):
        super().__init__()

        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        self.mainwindow = mainwindow
        self.console_signal = console_signal
        self.command_file = '%s/command.txt'%TFile.CONFIG_PATH
        self.setWindowTitle("命令集")
        self.IntUi()

    def __del__(self):
        self.wait()

    def IntUi(self):
        mainLayout = QGridLayout()
      
        self.update()
        with open(self.command_file, 'r', encoding='utf-8') as f1:
            text = f1.read()
        text_list = text.split('\n')
        text_list = [i for i in text_list if i != ""]  # 去掉空
        for i, command in enumerate(text_list):
            commandstr = command.split('#')
            label = QLabel(commandstr[1])
            label.setStyleSheet("text-align:Right")
            self.button = QPushButton(commandstr[0])
            self.button.setStyleSheet("text-align:left;height:28px")
            self.button.clicked.connect(lambda ch, text=commandstr[0]: self.command_connect(text))
            mainLayout.addWidget(self.button, i, 1)
            mainLayout.addWidget(label, i, 0)
        self.setLayout(mainLayout)

    def command_connect(self, text):
        self.console_signal.emit('已拷贝:%s' % text, 'lime')
        text = str(text).replace('\\n', '\n')
        pyperclip.copy(text)
        self.destroy()

    def update(self):
        self.update_command_thread = UpdateCommandThread()
        self.update_command_thread.start()

    def closeEvent(self, event):
        print('#########')
        self.update_command_thread.quit()
        self.update_command_thread.terminate()



class UpdateCommandThread(QThread):
    def run(self):
        self.command_file = 'C:/TestTime/command.txt'
        try:
            r = requests.get('https://abf.qjdedsc.com/?a=getT2')
        except:
            print('网络异常')
            return
        lists = r.text.replace('<meta charset=\'utf-8\'/>', '').split('\n')
        with open(self.command_file, 'r', encoding='utf-8') as f:
            strs = f.read()
        for t in lists:
            if strs.find(t) == -1:
                with open(self.command_file, "a", encoding='utf-8') as file:
                    file.write('\n' + t + '\n')
