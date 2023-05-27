import json

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QListWidget, QLabel, QListWidgetItem, QCheckBox, QFrame, QHBoxLayout

from compoment.atx2agent.core.common.analyze_case import ParseCase
from compoment.atx2agent.core.models.model import CaseDto
from ui.test.model.signal import CaseManagerSignal
from utils.fileutils import get_py_path

test_case = ParseCase()
import ui.test.globalvar as gl
class CaseManagerView(QFrame):
    def __init__(self,caseManagerModule=None, parent=None):
        super(CaseManagerView, self).__init__(parent)
        self.caseManagerModule=caseManagerModule
        self.caseManagerSignal = CaseManagerSignal()
        self.caseManagerModule.addCaseSignal.connect(self.update_case_list)
        self.caseManagerModule.clear_case_list_signal.connect(self.clear_case_list)
        self.py_case_list =[]
        self.file_info_list = []  #py文件和对应路径
        self.init_ui()

    def init_ui(self):
        self.case_layout = QHBoxLayout()
        self.setFrameStyle(QFrame.Box)
        self.case_layout.addWidget(QLabel("测试用例"))
        self.setLayout(self.case_layout)
        self.case_list_widget = QListWidget()
        self.case_layout.addWidget(self.case_list_widget)

    def _add_yamlcase_to_list(self,item,column):
        if item.childCount() == 0:
            case_name = item.text(0)
            case_id = item.text(1)
            # 根据case_id 在整个导入的yaml文件中查找对应的case,并打包加入到用例中
            suites= gl.get_value('suites')
            test_json_list = test_case.get_case_info_by_case_id(case_id, suites)
            unique_json_list = []
            for i in test_json_list:
                test_dict_list = json.loads(i)
                if test_dict_list.get("caseId") not in unique_json_list:
                    unique_json_list.append(json.dumps(test_dict_list))
            if len(unique_json_list) > 0:
                new_json = list(set(unique_json_list))
                self.case_list_widget.addItems(new_json)
        else:
            for i in range(item.childCount()):
                child = item.child(i)
                self._add_yamlcase_to_list(child, column)

    def _add_pycase_to_list(self,item,column):
        # 获取用例名称
        if item.childCount() == 0:
            case_name = item.text(0)
            self.py_case_list.append(case_name)
            self.case_list_widget.addItems(list(set(self.py_case_list)))
            self.case_list_widget.sortItems()
        else:
            for i in range(item.childCount()):
                child = item.child(i)
                self._add_pycase_to_list(child, column)
        path = item.data(0, Qt.UserRole)
        if path:
            # 将这个path 转换为正确的路径
            path = path.replace("/", "\\")
        child_count = item.childCount()
        file_list = []
        for i in range(child_count):
            child_item = item.child(i)
            child_text = child_item.text(0)
            file_list.append(child_text)
        # 将路径和对应的py列表保存为一组
        file_info = (path, file_list)
        if file_info:
            path, file_list = file_info
            if path is not None and file_list is not None:
                self.list_item = QListWidgetItem()
                if file_info not in self.file_info_list:
                    self.file_info_list.append(file_info)

    def clear_case_list(self):
        self.case_list_widget.clear()
        self.py_case_list.clear()

    def update_case_list(self,case_type,item,column):
        self.case_list_widget.clear()
        if case_type =="yaml":
            print("case_type------>", case_type)
            self._add_yamlcase_to_list(item,column)
            # 解除信号槽
        elif case_type =="py":
           print("case_type------>", case_type)
           self._add_pycase_to_list(item,column)

        # self.case_list_widget.clear()
        # for case in cases:
        #     item = QListWidgetItem()
        #     checkbox = QCheckBox(case)
        #     self.case_list_widget.addItem(item)
        #     self.case_list_widget.setItemWidget(item, checkbox)

            # 清空list列表
            # self.test_case_list_view.clear()

    def get_po_py_case_list(self):
        po_py_case_list = []
        if len(self.file_info_list) > 0:
            for case_path_list in self.file_info_list:  # 获取用例的路径和用例列表
                case_p, case_l = case_path_list
                p = get_py_path(case_p, case_l)
                # 如果列表没有po_py_case_list，则加到列表中
                if p not in po_py_case_list:
                    po_py_case_list.append(p)
        return po_py_case_list

    def get_selected_cases(self):
        selected_cases = []
        for index in range(self.case_list_widget.count()):
            item = self.case_list_widget.item(index)
            # checkbox = self.case_list_widget.itemWidget(item)
            # if checkbox.isChecked():
           # selected_cases.append(checkbox.text())
            selected_cases.append(item.text())
        return selected_cases

    def get_test_case_list_view(self):
        """
        获取用例列表视图中的用例数
        @return: 返回用例的列表集合
        """
        new_case_list = []
        for i in range(self.case_list_widget.count()):
            case_json = self.case_list_widget.item(i).text()
            new_case_list.append(CaseDto.from_json(case_json))
        return new_case_list


class CaseManagerController:
    def __init__(self, case_manager_view):
        self.case_manager_view = case_manager_view

    def update_case_list(self, cases):
        self.case_manager_view.update_case_list(cases)

    def get_selected_cases(self):
        return self.case_manager_view.get_selected_cases()

    def get_po_py_case_list(self):
        return self.case_manager_view.get_po_py_case_list()

    def get_test_case_list_view(self):
        return self.case_manager_view.get_test_case_list_view()

