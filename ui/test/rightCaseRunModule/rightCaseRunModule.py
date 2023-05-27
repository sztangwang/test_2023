from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QGroupBox, QVBoxLayout
from ui.test.rightCaseRunModule.rightDeviceManagerModule import DeviceManagerView, DeviceManagerController
from ui.test.rightCaseRunModule.taskManagerModule import TaskManagerView, TaskManagerController
from ui.test.rightCaseRunModule.taskTypeModule import TaskTypeModule, TaskTypeController
from ui.test.rightCaseRunModule.testCaseModule import CaseManagerView, CaseManagerController
from ui.test.rightCaseRunModule.testEngineModule import TestEngineModule
from ui.test.rightCaseRunModule.testTaskRunModule import TestTaskRunModule

class CaseRunModule(QGroupBox):
    def __init__(self,caseManagerModule=None,adbConnectionDeviceList=None, parent=None):
        super(CaseRunModule, self).__init__(parent)
        self.caseManagerModule = caseManagerModule
        self.adbConnectionDeviceList = adbConnectionDeviceList
        self.init_ui()
    def init_ui(self):
        self.caseRunLayout = QVBoxLayout()
        self.caseRunLayout.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.setLayout(self.caseRunLayout)
        self.setStyleSheet("font:12px")
        self.deviceManagerView = DeviceManagerView(self.adbConnectionDeviceList)
        self.deviceManagerController = DeviceManagerController(self.deviceManagerView)
        self.taskTypeView = TaskTypeModule()
        self.testEngineModule = TestEngineModule()
        self.caseManagerView = CaseManagerView(self.caseManagerModule)
        self.caseManagerController = CaseManagerController(self.caseManagerView)
        self.taskManagerView = TaskManagerView(self.caseManagerModule)
        self.taskManagerController = TaskManagerController(self.taskManagerView)
        self.taskTypeController = TaskTypeController(self.taskTypeView)
        self.testTaskRunModule = TestTaskRunModule(self.caseManagerController,self.deviceManagerController,
                                                   self.taskTypeController,self.taskManagerController)
        self.caseRunLayout.addWidget(self.deviceManagerView)
        self.caseRunLayout.addWidget(self.taskTypeView)
        self.caseRunLayout.addWidget(self.testEngineModule)
        self.caseRunLayout.addWidget(self.caseManagerView)
        self.caseRunLayout.addWidget(self.taskManagerView)
        self.caseRunLayout.addWidget(self.testTaskRunModule)
