from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QFrame, QVBoxLayout, QLabel, QLineEdit
class MiddleCaseDetailCaseDescFrame(QFrame):
    def __init__(self, parent=None):
        super(MiddleCaseDetailCaseDescFrame, self).__init__(parent)
        self.init_ui()
    def init_ui(self):
        ############ 右侧顶部第3行显示################
        self.caseDescLayout = QVBoxLayout()  # 顶部第二行水平布局
        self.caseDescLayout.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.setLayout(self.caseDescLayout)

        ########## 用例描述 ############
        self.detail_case_desc_label = QLabel()
        self.detail_case_desc_label.setText("用例描述：")
        self.detail_case_desc_edit = QLineEdit()
        self.detail_case_desc_edit.setText("用例描述显示在这里.....")

        self.detail_case_var_label = QLabel()
        self.detail_case_var_label.setText("用例变量：")
        self.caseDescLayout.addWidget(self.detail_case_desc_label)
        self.caseDescLayout.addWidget(self.detail_case_desc_edit)
        self.caseDescLayout.addWidget(self.detail_case_var_label)

    def setCaseDesc(self,caseDesc):
        self.detail_case_desc_edit.setText(caseDesc)

# 定义中间用例详情的用例描述模块数据处理类，类似mvc 中的model和controller
class MiddleCaseDetailCaseDescFrameModel():
    def __init__(self):
        pass
    def getCaseDesc(self):
        return "用例描述显示在这里....."


class MiddleCaseDetailCaseDescFrameController():
    def __init__(self,view):
        self.view=view
        self.model=MiddleCaseDetailCaseDescFrameModel()
    def setCaseDesc(self):
        self.view.setCaseDesc(self.model.getCaseDesc())