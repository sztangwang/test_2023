import cgitb
import sys
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication
from qt_material import apply_stylesheet
from ui.base.baseWindow import BaseWindow
from utils import fileutils
from common.logger import Logger
logger = Logger(level="info").logger


def showGui():
    app = QApplication(sys.argv)
    extra = {
        # Button colors
        'danger': '#dc3545',
        'warning': '#ffc107',
        'success': '#17a2b8',
        # Font
        'font_size': '12px',
        'line_height': '12px',
        
    }
    cgitb.enable(format='text')
    apply_stylesheet(app, 'dark_teal.xml', invert_secondary=True, extra=extra)
    w = BaseWindow()
    w.resize(1920, 1080)
    w.setWindowTitle("Anget")
    w.setWindowIcon(QIcon(fileutils.getResPath("images", "hollyland.png")))
    w.show()
    sys.exit(app.exec_())


def startAgentService(testSuitFiles: list, testDevices: list, testReportPath: str):

    pass


if __name__ == '__main__':
    showGui()
  
