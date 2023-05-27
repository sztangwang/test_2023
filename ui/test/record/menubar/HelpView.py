
from PyQt5.QtWidgets import QWidget, QAction

from ui.test.record.menubar.AboutView import AboutView
from ui.test.record.menubar.Update import Update


class HelpView(QWidget):
    def __init__(self, mainwindow):
        super().__init__()
        self.mainwindow = mainwindow
    
        self.HelpUi()

    def HelpUi(self):
        self.Help = self.mainwindow.menuBars.addMenu("Help")
        self.updatas = QAction('Check for updatas...', self)
        self.About = QAction('About', self)
        self.Help.addAction(self.updatas)
        self.Help.addAction(self.About)
        self.updatas.triggered.connect(self.updatas_connect)
        self.About.triggered.connect(self.about_connect)
        self.about_view = AboutView()
       

    def updatas_connect(self):
        self.update.start()
        self.update.exec_()

    def about_connect(self):
        self.about_view.show()

