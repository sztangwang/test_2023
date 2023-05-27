from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QFrame, QHBoxLayout, QLabel, QGroupBox, QRadioButton, QMessageBox

from compoment.atx2agent.core.task.task_manage import TaskType


class TaskTypeModule(QFrame):
    def __init__(self, parent=None):
        super(TaskTypeModule, self).__init__(parent)
        self.init_ui()

    def init_ui(self):
        self.taskTypeLayout = QHBoxLayout()
        self.taskTypeLayout.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.setLayout(self.taskTypeLayout)
        ########## 选择测试类型 ############
        self.case_test_label = QLabel()
        self.case_test_label.setText("测试类型：")
        self.testModelGbx = QGroupBox()
        self.gbxLayout = QHBoxLayout(self.testModelGbx)

        po_ui_test = QRadioButton(TaskType.PO_UI_TEST)
        kw_ui_test = QRadioButton(TaskType.KW_UI_TEST)
        smoke_test = QRadioButton(TaskType.SMOKE_TEST)
        hard_test = QRadioButton(TaskType.HARDWARE_TEST)

        other_test = QRadioButton(TaskType.NONE)
        # 默认选中软件
        other_test.setChecked(True)
        self.testModelGbx.layout().addWidget(po_ui_test)
        self.testModelGbx.layout().addWidget(smoke_test)
        self.testModelGbx.layout().addWidget(kw_ui_test)
        self.testModelGbx.layout().addWidget(hard_test)
        self.testModelGbx.layout().addWidget(other_test)
        self.ware_list = [po_ui_test, kw_ui_test, smoke_test, hard_test, other_test]
        for btn in self.ware_list:
            btn.clicked.connect(self.change_model_func)
        self.taskTypeLayout.addWidget(self.case_test_label)
        self.taskTypeLayout.addWidget(self.testModelGbx)

    def change_model_func(self):
        testModel = [btn.text() for btn in self.ware_list if btn.isChecked()][0]
        return testModel

class TaskTypeController:
    def __init__(self, task_type_module):
        self.task_type_module = task_type_module

    def get_task_type(self):
        return self.task_type_module.change_model_func()