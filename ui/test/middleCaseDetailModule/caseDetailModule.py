from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QFrame, QGroupBox, QVBoxLayout
from ui.test.middleCaseDetailModule.caseDetailCaseDescModule import MiddleCaseDetailCaseDescFrame, \
    MiddleCaseDetailCaseDescFrameController
from ui.test.middleCaseDetailModule.caseDetailCaseDirModule import MiddleCaseDetailCaseDirFrame, \
    MiddleCaseDetailCaseDirFrameController
from ui.test.middleCaseDetailModule.caseDetailCaseNameModule import MiddleCaseDetailCaseNameFrame, \
    MiddleCaseDetailCaseNameFrameController
from ui.test.middleCaseDetailModule.caseDetailCaseStepModule import MiddleCaseDetailCaseStepFrame, \
    MiddleCaseDetailCaseStepFrameController
from ui.test.middleCaseDetailModule.caseDetailCaseVarModule import MiddleCaseDetailCaseVarFrame, \
    MiddleCaseDetailCaseVarFrameController

class MiddleCaseDetailFrame(QGroupBox):
    def __init__(self, parent=None):
        super(MiddleCaseDetailFrame, self).__init__(parent)
        self.init_ui()
    def init_ui(self):
        self.centerCaseDetailLayout = QVBoxLayout()
        self.centerCaseDetailLayout.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.setLayout(self.centerCaseDetailLayout)
        self.setStyleSheet("font:12px")
        self.middleCaseDetailCaseNameFrame=MiddleCaseDetailCaseNameFrame()
        self.middleCaseDetailCaseDirFrame = MiddleCaseDetailCaseDirFrame()
        self.middleCaseDetailCaseDescFrame = MiddleCaseDetailCaseDescFrame()
        self.middleCaseDetailCaseVarFrame = MiddleCaseDetailCaseVarFrame()
        self.middleCaseDetailCaseStepFrame = MiddleCaseDetailCaseStepFrame()
        self.caseDetailCaseNameController =MiddleCaseDetailCaseNameFrameController(self.middleCaseDetailCaseNameFrame)
        self.caseDetailCaseNameController.setCaseName()
        self.caseDetailCaseDirController = MiddleCaseDetailCaseDirFrameController(self.middleCaseDetailCaseDirFrame)
        self.caseDetailCaseDirController.setCaseDir()
        self.caseDetailCaseDirController.setCaseLevel()
        self.caseDetailCaseDirController.setCaseStatus()
        self.caseDetailCaseDirController.setCaseType()
        self.caseDetailCaseDescController = MiddleCaseDetailCaseDescFrameController(self.middleCaseDetailCaseDescFrame)
        self.caseDetailCaseDescController.setCaseDesc()
        self.caseDetailCaseVarController = MiddleCaseDetailCaseVarFrameController(self.middleCaseDetailCaseVarFrame)
        self.caseDetailCaseVarController.setCaseVarName()
        self.caseDetailCaseVarController.setCaseVarValue()
        self.caseDetailCaseVarController.setCaseVarDesc()
        self.caseDetailCaseStepController = MiddleCaseDetailCaseStepFrameController(self.middleCaseDetailCaseStepFrame)
        self.centerCaseDetailLayout.addWidget(self.middleCaseDetailCaseNameFrame)
        self.centerCaseDetailLayout.addWidget(self.middleCaseDetailCaseDirFrame)
        self.centerCaseDetailLayout.addWidget(self.middleCaseDetailCaseDescFrame)
        self.centerCaseDetailLayout.addWidget(self.middleCaseDetailCaseVarFrame)
        self.centerCaseDetailLayout.addWidget(self.middleCaseDetailCaseStepFrame)

