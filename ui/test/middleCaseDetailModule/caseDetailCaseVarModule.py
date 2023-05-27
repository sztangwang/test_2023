from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QFrame, QHBoxLayout, QLabel, QLineEdit
class MiddleCaseDetailCaseVarFrame(QFrame):
    def __init__(self, parent=None):
        super(MiddleCaseDetailCaseVarFrame, self).__init__(parent)
        self.init_ui()
    def init_ui(self):
        ############ 右侧顶部第4行显示################
        # self.topFrame2.setFixedSize(QDesktopWidget().availableGeometry().size().width()*0.7,100)
        self.caseVarLayout = QHBoxLayout()  # 顶部第二行水平布局
        self.caseVarLayout.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.setLayout(self.caseVarLayout)
        ########## 变量描述 ############
        self.detail_case_var_name_label = QLabel()
        self.detail_case_var_name_label.setText("变量名：")
        self.detail_case_var_name_edit = QLineEdit()
        self.detail_case_var_name_edit.setText("变量名称显示")
        self.detail_case_var_value_label = QLabel()
        self.detail_case_var_value_label.setText("变量值：")
        self.detail_case_var_value_edit = QLineEdit()
        self.detail_case_var_value_edit.setText("变量值显示")
        self.detail_case_var_desc_label = QLabel()
        self.detail_case_var_desc_label.setText("变量描述：")
        self.detail_case_var_desc_edit = QLineEdit()
        self.detail_case_var_desc_edit.setText("变量描述")
        self.caseVarLayout.addWidget(self.detail_case_var_name_label)
        self.caseVarLayout.addWidget(self.detail_case_var_name_edit)
        self.caseVarLayout.addWidget(self.detail_case_var_value_label)
        self.caseVarLayout.addWidget(self.detail_case_var_value_edit)
        self.caseVarLayout.addWidget(self.detail_case_var_desc_label)
        self.caseVarLayout.addWidget(self.detail_case_var_desc_edit)

    def setCaseVarName(self,caseVarName):
        self.detail_case_var_name_edit.setText(caseVarName)
    def setCaseVarValue(self,caseVarValue):
        self.detail_case_var_value_edit.setText(caseVarValue)
    def setCaseVarDesc(self,caseVarDesc):
        self.detail_case_var_desc_edit.setText(caseVarDesc)

class MiddleCaseDetailCaseVarFrameModel():
    def __init__(self):
        pass
    def getCaseVarName(self):
        return "变量名称显示"
    def getCaseVarValue(self):
        return "变量值显示"
    def getCaseVarDesc(self):
        return "变量描述"

class MiddleCaseDetailCaseVarFrameController():
    def __init__(self,view):
        self.view=view
        self.model=MiddleCaseDetailCaseVarFrameModel()
    def setCaseVarName(self):
        self.view.setCaseVarName(self.model.getCaseVarName())
    def setCaseVarValue(self):
        self.view.setCaseVarValue(self.model.getCaseVarValue())
    def setCaseVarDesc(self):
        self.view.setCaseVarDesc(self.model.getCaseVarDesc())