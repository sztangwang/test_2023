from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QFrame, QVBoxLayout, QLabel, QGridLayout, QTreeWidget, QTreeWidgetItem
from qtpy import QtWidgets, QtCore
from compoment.atx2agent.core.common.analyze_case import ParseCase

class MiddleCaseDetailCaseStepFrame(QFrame):
    def __init__(self, parent=None):
        super(MiddleCaseDetailCaseStepFrame, self).__init__(parent)
        self.init_ui()
    def init_ui(self):
        ############ 右侧顶部第5行显示################
        # self.topFrame2.setFixedSize(QDesktopWidget().availableGeometry().size().width()*0.7,100)
        self.caseStepLayout = QVBoxLayout()  # 顶部第二行水平布局
        self.caseStepLayout.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.setLayout(self.caseStepLayout)
        ########## 用例步骤详情 ############
        self.detail_case_step_label = QLabel()
        self.detail_case_step_label.setText("用例步骤：")
        self.detailCaseStepWidget = QtWidgets.QWidget()
        self.detailCaseStepWidgetGridlayout = QGridLayout(self.detailCaseStepWidget)
        self.case_step_tree = QTreeWidget(self.detailCaseStepWidget)
        self.case_step_tree.setStyleSheet("font:12px")
        self.case_step_tree.setSortingEnabled(False)
        self.detailCaseStepWidgetGridlayout.addWidget(self.case_step_tree)
        # #########  定义项目用例树结构 ###########
        # self.case_project_tree = QTreeWidget()
        self.case_step_tree.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.case_step_tree.setAutoScroll(True)
        self.case_step_tree.setProperty("showDropIndicator", False)
        self.case_step_tree.setRootIsDecorated(True)
        self.case_step_tree.setAllColumnsShowFocus(False)
        self.case_step_tree.setExpandsOnDoubleClick(False)
        self.case_step_tree.setObjectName("casetreeWidget")
        self.case_step_tree.setColumnCount(4)
        self.case_step_tree.setHeaderLabels(['步骤', '步骤名称', '步骤描述', '扩展'])
        self.case_step_tree.setColumnWidth(0, 200)
        self.case_step_tree.setColumnWidth(1, 300)
        self.case_step_tree.setColumnWidth(2, 300)
        self.case_step_tree.setColumnWidth(3, 300)
        self.caseStepLayout.addWidget(self.detail_case_step_label)
        self.caseStepLayout.addWidget(self.detailCaseStepWidget)

        projectCase =MiddleCaseDetailCaseStepFrameModel().getCaseData()
        self.initCaseTree(self.case_step_tree, projectCase)

    def initCaseTree(self, case_tree_widget: QTreeWidget, rootData):
        rootList = []
        if rootData is None:
            return
        else:
            for i, _modules in enumerate(rootData.project.modules):
                # 获取用例集
                for i, _case in enumerate(_modules.module.cases):
                    root = QTreeWidgetItem(case_tree_widget)
                    case = _case.case
                    root.setText(0, case.name)  # 用例名称
                    # 获取 用例描述
                    globalval = case.globalVal
                    prestep = case.presteps
                    poststep = case.poststeps
                    steps = case.steps
                    if i == 0:
                        # 设置选中状态
                        root.setCheckState(0, Qt.Checked)
                        case_tree_widget.expandAll()  # 展开所有节点
                    else:
                        root.setCheckState(0, Qt.Unchecked)
                    # 定义globalVal 节点
                    globalVal = QTreeWidgetItem()
                    globalVal.setText(0, '全局变量：')
                    for _globalval in globalval:
                        globalvalItem = QTreeWidgetItem()
                        globalvalItem.setText(0, _globalval.name)
                        globalvalItem.setText(1, _globalval.value)
                        globalvalItem.setCheckState(0, Qt.Checked)  # 设置选项已被选中状态
                        globalVal.addChild(globalvalItem)
                    root.addChild(globalVal)
                    preStepsItem = QTreeWidgetItem()
                    preStepsItem.setText(0, "前置步骤：")
                    self._parserStep(prestep, preStepsItem)
                    postStepsItem = QTreeWidgetItem()
                    postStepsItem.setText(0, "后置步骤：")
                    self._parserStep(poststep, postStepsItem)
                    stepsItem = QTreeWidgetItem()
                    stepsItem.setText(0, "测试步骤：")
                    self._parserStep(steps, stepsItem)
                    root.addChild(preStepsItem)
                    root.addChild(postStepsItem)
                    root.addChild(stepsItem)
                    rootList.append(root)
            case_tree_widget.addTopLevelItems(rootList)  # 将根节点添加到树控件中
            case_tree_widget.clicked.connect(self.onTreeClicked)  # 绑定单击事件

    def _parserStep(self, steps, qTreeStepItem: QTreeWidgetItem):
        for i, _step in enumerate(steps):
            prestepItem = QTreeWidgetItem()
            prestepItem.setText(0, '步骤{}：'.format(i + 1))
            qTreeStepItem.addChild(prestepItem)
            step = _step.step
            stepItem = QTreeWidgetItem()
            stepItem.setText(0, '执行步骤：')
            actionItem = QTreeWidgetItem()
            actionItem.setText(0, step.action)
            actionItem.setText(1, step.desc)
            actionItem.setText(2, step.name)
            stepItem.addChild(actionItem)
            prestepItem.addChild(stepItem)
            if step.params:
                for _param_key, _param_v in step.params.items():
                    paramItem = QTreeWidgetItem()
                    paramItem.setText(0, _param_key)
                    # 如果值是double,float,int类型，就转换成str类型
                    if isinstance(_param_v, (float, int)):
                        _param_v = str(_param_v)
                    paramItem.setText(1, _param_v)
                    actionItem.addChild(paramItem)
            locators = step.locators
            if locators is not None:
                locatorItems = QTreeWidgetItem()
                locatorItems.setText(0, '定位元素：')
                prestepItem.addChild(locatorItems)
                locatorItem = QTreeWidgetItem()
                for _locator in locators:
                    locatorItem.setText(0, _locator.name)
                    locatorItem.setText(1, _locator.locateDesc)
                    locatorItem.setText(2, _locator.locatorType)
                    locatorItem.setText(3, _locator.locatorValue)
                    locatorItems.addChild(locatorItem)

    def onTreeClicked(self, index):
        item = self.case_project_tree.currentItem()
        print(item.text(0))
class MiddleCaseDetailCaseStepFrameModel():
    def __init__(self):
        pass

    # 获取测试用例数据
    def getCaseData(self):
        test_case = ParseCase()
        project_cases = test_case.get_project_dto()
        return project_cases

class MiddleCaseDetailCaseStepFrameController():
    def __init__(self,view):
        self.view=view
        self.model=MiddleCaseDetailCaseStepFrameModel()

