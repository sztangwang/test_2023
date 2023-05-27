from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QFrame, QHBoxLayout, QLabel
class MiddleCaseDetailCaseDirFrame(QFrame):
    def __init__(self, parent=None):
        super(MiddleCaseDetailCaseDirFrame, self).__init__(parent)
        self.init_ui()
    ########### 右侧顶部第二行显示#################
    def init_ui(self):
        self.caseDirLayout = QHBoxLayout()  # 顶部第二行水平布局
        self.caseDirLayout.setAlignment(Qt.AlignLeft)
        self.setLayout(self.caseDirLayout)
        self.case_dir_label = QLabel()  # 用例名称
        self.case_dir_label.setText("用例目录结构：[项目1/模块名称1/添加直播和开启直播]")
        self.caseDirLayout.addWidget(self.case_dir_label)

        self.detail_case_level_label = QLabel()  # 用例等级
        self.detail_case_level_label.setText("用例等级：[PO]")
        self.caseDirLayout.addWidget(self.detail_case_level_label)

        self.detail_case_status_label = QLabel()
        self.detail_case_status_label.setText("用例状态：[PO]")
        self.caseDirLayout.addWidget(self.detail_case_status_label)

        self.detail_case_tpye_label = QLabel()
        self.detail_case_tpye_label.setText("用例类型：[UI测试用例]")
        self.caseDirLayout.addWidget(self.detail_case_tpye_label)

    def setCaseDir(self,caseDir):
        self.case_dir_label.setText(caseDir)

    def setCaseLevel(self,caseLevel):
        self.detail_case_level_label.setText(caseLevel)

    def setCaseStatus(self,caseStatus):
        self.detail_case_status_label.setText(caseStatus)

    def setCaseType(self,caseType):
        self.detail_case_tpye_label.setText(caseType)

class MiddleCaseDetailCaseDirFrameModel():
    def __init__(self):
        pass
    def getCaseDir(self):
        return "用例目录结构：[项目1/模块名称1/添加直播和开启直播]"
    def getCaseLevel(self):
        return "用例等级显示在这里..."
    def getCaseStatus(self):
        return "用例状态显示在这里..."
    def getCaseType(self):
        return "用例类型显示在这里..."

class MiddleCaseDetailCaseDirFrameController():
    def __init__(self,view):
        self.view=view
        self.model=MiddleCaseDetailCaseDirFrameModel()
    def setCaseDir(self):
        self.view.setCaseDir(self.model.getCaseDir())
    def setCaseLevel(self):
        self.view.setCaseLevel(self.model.getCaseLevel())
    def setCaseStatus(self):
        self.view.setCaseStatus(self.model.getCaseStatus())
    def setCaseType(self):
        self.view.setCaseType(self.model.getCaseType())
