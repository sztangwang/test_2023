#!/usr/bin/python
# -*- coding: UTF-8 -*-
import sys
from PyQt5.QtWidgets import *
from MainWindow import Ui_MainWindow
if __name__ == "__main__":
    App = QApplication(sys.argv)
    ex = Ui_MainWindow()
    ex.show()
    sys.exit(App.exec_())