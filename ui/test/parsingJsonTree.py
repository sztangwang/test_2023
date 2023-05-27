import PyQt5
import chardet as chardet
from PyQt5.QtCore import Qt
from PyQt5 import QtWidgets
from engineio import json

from compoment.atx2agent.core.common.analyze_case import ParseCase


class ItemWidget(QtWidgets.QWidget):
    """自定义的item"""

    def __init__(self, text, badge, *args, **kwargs):
        super(ItemWidget, self).__init__(*args, **kwargs)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(QLabel(text, self, styleSheet='color: red;'))
        # layout.addSpacerItem(QSpacerItem(
        #     60, 1, QSizePolicy.Maximum, QSizePolicy.Minimum))
        # if badge and len(badge) == 2:  # 后面带颜色的标签
        #     layout.addWidget(QLabel(
        #         badge[0], self, alignment=Qt.AlignCenter,
        #     ))


class JsonTreeWidget(PyQt5.QtWidgets.QTreeWidget):



    def __init__(self, *args, **kwargs):
        super(JsonTreeWidget, self).__init__(*args, **kwargs)
        self.setEditTriggers(self.NoEditTriggers)
        self.header().setVisible(False)
        # 帮点单击事件
        self.itemClicked.connect(self.onItemClicked)

    def onItemClicked(self, item):
        """item单击事件"""
        pass

    def parseData(self, datas, parent=None):
        """解析json数据"""
        # 解析datas cases 里面的数据
        for data in datas.get('cases', []):
            caseName = data.get('caseName', '')
            caseDesc = data.get('caseDesc', [])
            globalVal = data.get('globalVal', [])
            preSteps = data.get('preSteps', [])
            postSteps = data.get('postSteps', [])
            steps = data.get('steps', [])
            # 生成item
            _item = QTreeWidgetItem(parent)
           # _item.setIcon(0, QIcon(data.get('icon', '')))
            _widget = ItemWidget(
                caseName,
                caseDesc,
                # globalVal,
                # preSteps,
                # postSteps,
                # steps,
                self
            )
            self.setItemWidget(_item, 0, _widget)

            # # 解析儿子
            # if items:
            #     self.parseData(items, _item)

    def loadData(self, path):
        """加载json数据"""
        datas = open(path, 'rb').read()
        datas = datas.decode(chardet.detect(datas).get('encoding', 'utf-8'))
        self.parseData(json.loads(datas), self)

    def setUpUi(self):
        test_case = ParseCase()
        cases = test_case.get_project_dto()
        print("cases------>",cases)
        print("project_cases", cases.project.name)
        self.treeCase = QTreeWidget()
        # 设置列数
        self.treeCase.setColumnCount(6)
        # 设置头部
        self.treeCase.setHeaderLabels(['', '用例名称', '用例描述', '全局变量', '前置步骤', '后置步骤', '步骤'])
        # 设置第一列的宽度
        self.treeCase.setColumnWidth(0, 300)
        rootList = []
        for _case in cases.cases:
            case = _case.case
            root = QTreeWidgetItem(self.treeCase)
            root.setText(0, case.name)
            root.setText(1, case.desc)
            globalval = case.globalVal
            preSteps = case.presteps
            postSteps = case.poststeps
            steps = case.steps
            for _globalval in globalval:
                globalvalItem = QTreeWidgetItem()
                globalvalItem.setText(0, _globalval.name)
                globalvalItem.setText(1, _globalval.value)
                globalvalItem.setCheckState(0, Qt.Checked)  # 设置选项已被选中状态
                root.addChild(globalvalItem)
            for _prestep in preSteps:
                step = _prestep.step
                actionItem = QTreeWidgetItem()
                actionItem.setText(0, step.action)
                for _param_key,_param_v in step.params.items():
                    paramItem = QTreeWidgetItem()
                    paramItem.setText(0, _param_key)
                    # 如果值是double,float,int类型，就转换成str类型
                    if isinstance(_param_v, (float, int)):
                        _param_v = str(_param_v)
                    paramItem.setText(1,_param_v)
                    actionItem.addChild(paramItem)
                root.addChild(actionItem)
                locators = step.locators
                if locators is not None:
                    print("locators ---->>> " + locators)
                    for _locator in locators:
                        locatorItem = QTreeWidgetItem()
                        locatorItem.setText(0, _locator.name)
                        locatorItem.setText(1, _locator.locateDesc)
                        root.addChild(locatorItem)

            prestepItem = QTreeWidgetItem()
            prestepItem.setText(0, "preSteps")
            prestepItem.setText(1, "preSteps")
            root.addChild(prestepItem)
            root.setText(3, "preSteps")
            root.setText(4, "postSteps")
            root.setText(5, "steps")
            rootList.append(root)

        self.treeCase.addTopLevelItems(rootList) # 将根节点添加到树控件中
        self.treeCase.expandAll()  # 展开所有节点
        self.treeCase.clicked.connect(self.onTreeClicked)  # 绑定单击事件



    def onTreeClicked(self, index):
        item = self.treeCase.currentItem()
        print(item.text(0))



if __name__ == '__main__':
    import sys
    from PyQt5.QtWidgets import QApplication, QTreeWidgetItem, QTreeWidget, QHBoxLayout, QLabel

    app = QApplication(sys.argv)

    w = JsonTreeWidget()
    w.show()
    w.setUpUi()
   # w.loadData(r'D:\python-workspace\Windows_Agent\compoment\atx2agent\core\testcases\case_demo.json')
    sys.exit(app.exec_())