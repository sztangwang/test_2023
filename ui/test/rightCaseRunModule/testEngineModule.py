from PyQt5.QtWidgets import QFrame, QLabel, QHBoxLayout


class TestEngineModule(QFrame):
    def __init__(self, parent=None):
        super(TestEngineModule, self).__init__(parent)
        self.initUI()

    def initUI(self):
        self.testEngineLayout = QHBoxLayout()
        self.setFrameStyle(QFrame.Box)
        self.testEngineLayout.addWidget(QLabel("测试引擎"))
        self.engineLaybel = QLabel("ATX")
        self.testEngineLayout.addWidget(self.engineLaybel)
        self.setLayout(self.testEngineLayout)

    def getEngine(self):
        return self.engineLaybel.text()

    def setEngine(self, engine):
        self.engineLaybel.setText(engine)