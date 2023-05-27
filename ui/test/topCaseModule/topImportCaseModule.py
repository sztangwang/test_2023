from PyQt5.QtCore import QDir, Qt, pyqtSignal, QObject
from PyQt5.QtWidgets import QFrame, QHBoxLayout, QLabel, QComboBox, QPushButton, QFileDialog
from qtpy import QtWidgets

from ui.test.model.signal import CaseManagerSignal


# 顶部用例导入模块
class TopImportCaseFrame(QFrame):
    def __init__(self, parent=None):
        super(TopImportCaseFrame, self).__init__(parent)
        self.importCaseModel= TopImportCaseFrameModel()
        self.signal = CaseManagerSignal()
        self.init_ui()
    def init_ui(self):
        self.topImportCaseLayout= QHBoxLayout()  # 顶部第二行水平布局
        self.topImportCaseLayout.setAlignment(Qt.AlignLeft)
        self.setLayout(self.topImportCaseLayout)
        ################# 导入用例 #############
        self.case_import_label = QLabel()
        self.case_import_label.setText("选择导入用例：")
        self.case_import_comboBox = QComboBox()
        self.case_import_comboBox.setObjectName("comboBox")
        self.case_import_comboBox.setFixedSize(150, 30)
        self.case_import_line_edit = QtWidgets.QLineEdit()
        self.case_import_button = QPushButton("导入")

        self.topImportCaseLayout.addWidget(self.case_import_label)
        self.topImportCaseLayout.addWidget(self.case_import_comboBox)
        self.topImportCaseLayout.addWidget(self.case_import_line_edit)
        self.topImportCaseLayout.addWidget(self.case_import_button)

        self.case_import_button.clicked.connect(self.importCase)

    def setIpmortCaseName(self,caseName):
        self.case_import_line_edit.setText(caseName)

    def setCaseTypeImportComboBox(self,importList):
        for i in importList:
            self.case_import_comboBox.addItem(i)

    def importCase(self):
        file_extension = self.case_import_comboBox.currentText()
        curPath = QDir.currentPath() + r"\compoment\atx2agent\core"
        if file_extension == "导入关键字用例(.yaml)":
            file_file_filter = "(*.yaml)"
            file_path, filetype = QFileDialog.getOpenFileName(self, "选取文件", curPath, filter=file_file_filter)
            self.setIpmortCaseName(file_path)
            self.signal.importCaseSignal.emit("yaml", file_path)
            self.signal.clear_task_list_signal.emit() # 发送清空任务列表信号
            print("发送清空任务列表信号")
        elif file_extension == "导入PO用例(.py)":
            selected_dir = QFileDialog.getExistingDirectory(self, "选取文件夹", curPath, QFileDialog.ShowDirsOnly)
            if selected_dir:
                self.signal.importCaseSignal.emit("py", selected_dir)
                self.signal.clear_task_list_signal.emit() # 发送清空任务列表信号
        else:
            return


# 定义顶部用例导入模块数据处理类，类似mvc 中的model和controller
class TopImportCaseFrameModel():
    def __init__(self):
        pass
    def getCaseName(self):
        return "用例名称显示在这里..."

    def getCaseType(self):
        caseTypeList=["导入关键字用例(.yaml)","导入PO用例(.py)"]
        return caseTypeList


class TopImportCaseFrameController():
    def __init__(self,view):
        self.view=view
        self.model=TopImportCaseFrameModel()
    def setIpmortCaseName(self):
        self.view.setIpmortCaseName(self.model.getCaseName())
    def setCaseTypeImportComboBox(self):
        self.view.setCaseTypeImportComboBox(self.model.getCaseType())

