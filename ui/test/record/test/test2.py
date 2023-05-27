from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
import sys, math

class splitter(QWidget):
    def __init__(self):
        super(splitter, self).__init__()
        self.setWindowTitle("拖动控件之间的边界")
        self.setGeometry(300,300,300,200)

        topleft=QFrame()
        topleft.setFrameShape(QFrame.StyledPanel)

        bottom = QTextEdit("编辑器")

        #设置所包含的控件之间可以水平拖动，基本设置为水平布局
        splitter1=QSplitter(Qt.Horizontal)

        text=QTextEdit("代码区")
        splitter1.addWidget(topleft)
        splitter1.addWidget(text)

        #设置默认的控件之间的大小距离
        splitter1.setSizes([100,200])

        #设置所包含的控件之间可以垂直拖动，设置我垂直布局
        splitter2= QSplitter(Qt.Vertical)

        text = QTextEdit()
        splitter2.addWidget(splitter1)
        splitter2.addWidget(bottom)

        h=QVBoxLayout()
        h.addWidget(splitter2)
        self.setLayout(h)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    p = splitter()
    p.show()
    sys.exit(app.exec_())