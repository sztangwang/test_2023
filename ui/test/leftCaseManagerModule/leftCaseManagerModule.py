import json
import os
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QFrame, QVBoxLayout, QGridLayout, QTreeWidget, QTreeWidgetItem, QListWidgetItem, QMessageBox
from qtpy import QtCore, QtWidgets

from compoment.atx2agent.core.common.analyze_case import ParseCase
from config.menuDataConfig import SuiteConfigData
from ui.test.model.signal import CaseManagerSignal
import ui.test.globalvar as gl

Suites = []
test_case = ParseCase()
class LeftCaseManagerModule(QFrame):
    def __init__(self,importCaseFrame=None, parent=None):
        super(LeftCaseManagerModule, self).__init__(parent)
        self.caseManagerSignal=CaseManagerSignal()
        self.addCaseSignal =self.caseManagerSignal.case_list_update_signal
        self.importCaseFrame=importCaseFrame
        self.clear_case_list_signal = self.caseManagerSignal.clear_case_list_signal
        self.importCaseFrame.signal.importCaseSignal.connect(self.importCase)

        self.init_ui()
    def init_ui(self):
        self.centerLeftLayout = QVBoxLayout()
        self.setLayout(self.centerLeftLayout)
        self.centerLeftContentWidget = QtWidgets.QWidget()
        self.centerLeftGridlayout = QGridLayout(self.centerLeftContentWidget)
        self.case_project_tree = QTreeWidget(self.centerLeftContentWidget)
        self.case_project_tree.setStyleSheet("font:12px")
        self.case_project_tree.setSortingEnabled(False)
        self.centerLeftGridlayout.addWidget(self.case_project_tree)
        self.centerLeftLayout.addWidget(self.centerLeftContentWidget)
        self.case_project_tree.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.case_project_tree.setAutoScroll(True)
        self.case_project_tree.setProperty("showDropIndicator", False)
        self.case_project_tree.setRootIsDecorated(True)
        self.case_project_tree.setAllColumnsShowFocus(False)
        self.case_project_tree.setExpandsOnDoubleClick(False)
        self.case_project_tree.setObjectName("casetreeWidget")
        self.case_project_tree.setColumnCount(1)
        self.case_project_tree.setHeaderLabels(['用例管理'])
        self.case_project_tree.setColumnWidth(0, 300)

    def init_project_case(self, project_case_tree: QTreeWidget, rootData):
        project_name = rootData.project.name
        rootList = []
        root = QTreeWidgetItem(project_case_tree)
        root.setText(0, project_name)
        for i, _modules in enumerate(rootData.project.modules):
            module_name = _modules.module.name  # 获取模块名称
            module_item = QTreeWidgetItem()
            module_item.setText(0, module_name)
            root.addChild(module_item)
            # 获取用例集
            for i, _case in enumerate(_modules.module.cases):
                case_item = QTreeWidgetItem()
                case = _case.case
                # 获取 用例描述
                case_desc = case.desc
                case_item.setText(0, case_desc)
                case_item.setText(1, str(case.caseId))
                module_item.addChild(case_item)
        rootList.append(root)
        project_case_tree.addTopLevelItems(rootList)  # 将根节点添加到树控件中
        project_case_tree.itemDoubleClicked.connect(self.addCaseToList)
        # todo 这里有个坑，因为操作的是同一个对象树，所以会导致发送了2个信号。
    def addCaseToList(self, item, column):
        print("双击的格式是：yaml", item.text(0), "列：", column)
        self.addCaseSignal.emit("yaml",item, column)

    def importCase(self,type,filePath):
        if type=="yaml":
            print("导入的格式是：yaml", filePath)
            self._readYamlCase(filePath)
        elif type=="py":
            print("导入的格式是：py", filePath)
            self._readPyCase(filePath)

    def _readYamlCase(self, file_path):
        self.case_project_tree.clear()
        self.clear_case_list_signal.emit()  # 发送清空用例列表的信号
        gl._init()
        suites = gl.get_value('suites')
        if file_path:
            suiteConfigData = SuiteConfigData()
            if suites is None:
                try:
                    gl.set_value("suites",suiteConfigData.readSuiteConfigData(file_path))
                except Exception as e:
                   # 弹出一个错误的提示框
                   QMessageBox.warning(self, "警告", "读取测试用例失败，测试用例yaml文件中的用例格式不对.参考正确格式：(testcases/case_demo2.yaml)",
                                       QMessageBox.Yes)
            suites_list =gl.get_value('suites')
            # 解析用例，并将数据展示在测试用例的树形列表中
            self.init_project_case(self.case_project_tree, suites_list)
        else:
            QMessageBox.warning(self, "警告", "读取测试用例失败,请检查是否是指定格式的测试用例.", QMessageBox.Yes)

    def _readPyCase(self, file_path):
        self.case_project_tree.clear()
        self.clear_case_list_signal.emit()  # 发送清空用例列表的信号
        # 解析用例，并将数据展示在测试用例的树形列表中
        self._init_py_case(file_path, self.case_project_tree)

    def _init_py_case(self, folder_path, py_case_tree: QTreeWidget):
        for root, dirs, files in os.walk(folder_path):
            if '__init__.py' in files:
                files.remove('__init__.py')
            if any(f.endswith('.py') for f in files):
                root_item = QTreeWidgetItem([os.path.basename(root), root])
                py_case_tree.addTopLevelItem(root_item)
                for file_name in files:
                    if file_name.endswith('.py'):
                        file_path = os.path.join(root)
                        file_item = QTreeWidgetItem([file_name])
                        root_item.setData(0, Qt.UserRole, file_path)
                        root_item.addChild(file_item)
        py_case_tree.itemDoubleClicked.connect(self._add_pycase_to_list)


    def _add_pycase_to_list(self, item, column):
        print("双击的格式是：py", item.text(0), "列：", column)
        self.addCaseSignal.emit("py", item, column)

    def onTreeClicked(self, index):
        item = self.treeCase.currentItem()
        print(item.text(0))