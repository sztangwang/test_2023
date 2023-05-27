from ui.test.leftCaseManagerModule.leftCaseManagerModule import LeftCaseManagerModule
from ui.test.middleCaseDetailModule.caseDetailModule import MiddleCaseDetailFrame
from ui.test.rightCaseRunModule.rightCaseRunModule import CaseRunModule
from ui.test.topCaseModule.topAllCaseModule import TopAllCaseFrame
from ui.test.topCaseModule.topImportCaseModule import TopImportCaseFrame, TopImportCaseFrameController
from ui.test.topCaseModule.topSearchCaseModule import TopSearchCaseFrame
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QFrame, QHBoxLayout, QDesktopWidget, QGroupBox
from qtpy import QtGui
from compoment.atx2agent.core.common.logs.log_uru import Logger
logger = Logger().get_logger

class SuitMenuLayout(QtWidgets.QWidget):
    def __init__(self, tuple_device=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tuple_device = tuple_device
        self.pool,self.adbConnectionDeviceList,self.runners= self.tuple_device
        self.initUI(self)

    def initUI(self, layout: QWidget):
     
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        # 设置窗口标题
        self.setWindowTitle('测试用例')
        # 根据屏幕大小设置窗口大小
        
        self.resize(QDesktopWidget().availableGeometry().size() * 100)

        self.mainLayout = QVBoxLayout()
        self.setLayout(self.mainLayout)

        # 顶部第一行的全部用例布局
        self.topAllCaseFrame=TopAllCaseFrame()

        # 顶部第二行用例搜索布局
        self.topSearchCaseFrame=TopSearchCaseFrame()
        self.topSearchCaseFrame.add_case_comboBox_label()

        ############# 第三行导入用例模块 ######################
        self.topImportCaseFrame= TopImportCaseFrame()
        self.topImportCaseFrameController=TopImportCaseFrameController(self.topImportCaseFrame)
        self.topImportCaseFrameController.setIpmortCaseName()
        self.topImportCaseFrameController.setCaseTypeImportComboBox()

        ############ 中间layout && frame 中间的用例管理布局，放一个tree的布局 ###############
        self.center_Frame = QFrame()
        self.center_layout = QHBoxLayout()
        self.center_Frame.setFrameStyle(QFrame.Box)
        self.center_Frame.setLayout(self.center_layout)
        ################ 左边用例管理################
        self.leftCaseManagerModule = LeftCaseManagerModule(self.topImportCaseFrame)

        ########### 中间用例详情 ###############
        self.middleCaseDetailFrame = MiddleCaseDetailFrame("用例详情")

        ########### 右侧显示执行用例 ###############
        self.caseRunModule= CaseRunModule(self.leftCaseManagerModule,self.adbConnectionDeviceList)

        # 整合左右布局
        self.center_layout.addWidget(self.leftCaseManagerModule)
        self.center_layout.addWidget(self.middleCaseDetailFrame)
        self.center_layout.addWidget(self.caseRunModule)

        self.center_layout.setStretch(1, 5)
        self.center_layout.setStretch(2, 3)

        self.mainLayout.addWidget(self.topAllCaseFrame)
        self.mainLayout.addWidget(self.topSearchCaseFrame)
        self.mainLayout.addWidget(self.topImportCaseFrame)
        self.mainLayout.addWidget(self.center_Frame)




