from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QHBoxLayout, QLabel, QFrame
class MiddleCaseDetailCaseNameFrame(QFrame):
    def __init__(self, parent=None):
        super(MiddleCaseDetailCaseNameFrame, self).__init__(parent)
        self.init_ui()
    def init_ui(self):
        ############ 右侧顶部第一行显示################
        self.caseNameLayout = QHBoxLayout()  # 顶部第二行水平布局
        self.caseNameLayout.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.setLayout(self.caseNameLayout)
        ########## 用例名称显示 ############
        self.case_name_label = QLabel()  # 用例名称
        self.case_name_label.setText("用例名称：")
        self.case_name_label_show = QLabel()
        self.caseNameLayout.addWidget(self.case_name_label)
        self.caseNameLayout.addWidget(self.case_name_label_show)

    def setCaseName(self,caseName):
        self.case_name_label_show.setText(caseName)

class MiddleCaseDetailCaseNameFrameModel():
    def __init__(self):
        pass
    def getCaseName(self):
        return "用例名称显示在这里..."

class MiddleCaseDetailCaseNameFrameController():
    def __init__(self,view):
        self.view=view
        self.model=MiddleCaseDetailCaseNameFrameModel()
    def setCaseName(self):
        self.view.setCaseName(self.model.getCaseName())