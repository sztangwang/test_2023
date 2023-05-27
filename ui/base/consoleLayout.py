
import sys
import logging
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QVBoxLayout
from PyQt5 import QtWidgets,QtGui
from PyQt5.QtCore import  pyqtSignal,QThread
from PyQt5.QtWidgets import QWidget

class consoleLayout(logging.Handler):
    def __init__(self, parent):
        super().__init__()
        self.Console = QtWidgets.QTextEdit(parent)
        self.IniUi()
        self.print_thread = print_thread()
        self.print_thread.signalForText.connect(self.out_print)
        
        sys.stdout = self.print_thread
        self.print_thread.start()
       
    def emit(self, record):
        msg = self.format(record)
        
        self.out_print( msg)

        
        

    def IniUi(self):
        self.console_layout = QVBoxLayout()
        self.console_layout.addWidget(self.Console)
        self.widget = QWidget()
        self.Console.document().setMaximumBlockCount(3000)  # 限制控制台显示行数

        self.setFormatter(logging.Formatter('%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s'))
        logging.getLogger().addHandler(self)
        logging.getLogger().setLevel(logging.DEBUG)
        
        self.widget.setLayout(self.console_layout)
        
    

    def out_print(self,text):
    

        if not text or text == ' ' or text == '\n':
            return
        elif [t for t in ['error','Fail','cannot','False'] if (text.lower()).count(t.lower()) > 0]:
            colour = 'red'
            
        elif [t for t in ['Pass','点击','打开','open','运行','开始测试',
                          'True','选择','Start','success'] if (text.lower()).count(t.lower()) > 0]:
            colour = 'lime'
        else:
            colour = 'white'
     
        cursor = self.Console.textCursor()
        cursor.movePosition(QtGui.QTextCursor.End)
        self.Console.append('<font size=3 color=%s>%s </font>' % (colour, text))
        self.Console.setTextCursor(cursor)
        self.Console.ensureCursorVisible()
        
     
     

        
 
class print_thread(QThread):
    signalForText = pyqtSignal(str)
    handle = -1 
    def __init__(self,data=None, parent=None):
        super(print_thread, self).__init__(parent)
        self.data = data

 
    def write(self, text):
     

        self.signalForText.emit(str(text))  # 发射信号