from PyQt5.Qt import *
from PyQt5 import QtWidgets,QtGui
from ui.test.record.Util import TFile
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel

class ConsoleView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.mainwindow = parent
        self.IniUi()

    def IniUi(self):
        self.console_layout = QVBoxLayout()
        self.console_label = QLabel('控制台显示')
        self.Console = QtWidgets.QTextEdit()
        self.Console.document().setMaximumBlockCount(2000)  # 限制控制台显示行数
        self.console_layout.addWidget(self.console_label)
        self.console_layout.addWidget(self.Console)
        self.setLayout(self.console_layout)

    def out_print(self,text):
        if not text or text == ' ' or text == '\n':
            return
        elif [t for t in ['异常','未','error','Fail','cannot',"无",
                          '空','无法','关闭','删除','清空','停止','False'] if (text.lower()).count(t.lower()) > 0]:
            colour = 'red'
      
        
        elif [t for t in ['Pass','点击','打开','open','运行','开始测试',
                          'True','选择'] if (text.lower()).count(t.lower()) > 0]:
            colour = 'lime'
       
        elif [t for t in ['休眠'] if (text.lower()).count(t.lower()) > 0]:
            colour = 'orange'
        else:
            colour = 'white'

        text = "{}-->{}".format(TFile.get_datetime('%m/%d/%H:%M:%S'),text)
        cursor = self.Console.textCursor()
        cursor.movePosition(QtGui.QTextCursor.End)
        self.Console.append('<font size=3 color=%s>%s </font>' % (colour, text))
        self.Console.setTextCursor(cursor)
        self.Console.ensureCursorVisible()
        filename = str('%s\control_Log_%s.txt' % (TFile.LOG_PATH,TFile.get_datetime('%Y%m%d')))
        with open(filename, 'a') as f:
            f.write(text + '\n')
      

        