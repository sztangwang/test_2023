from PyQt5 import QtCore
from PyQt5.Qt import *
from PyQt5.QtWidgets import QWidget, QAction
from config.menuDataConfig import *
from PyQt5.QtCore import Qt, QDir
from PyQt5.QtWidgets import  QHBoxLayout, QAction, QFileDialog

class menuBarLayout(QWidget):
    signal_fileTree = QtCore.pyqtSignal()
    console_signal = QtCore.pyqtSignal(str, str)
    select_insert_table_signal = QtCore.pyqtSignal(list)

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.mainwindow = parent
        

        self.fileMenu = self.mainwindow.mainMenu.addMenu("文件")
        self.configMenu = self.mainwindow.mainMenu.addMenu("配置")
        self.testMenu = self.mainwindow.mainMenu.addMenu("测试")
        self.helpMenu = self.mainwindow.mainMenu.addMenu("帮助")

        self.featureAction = QAction("功能测试")
        self.featureAction.setData(FeatureData)
        self.performanceAction = QAction("性能测试")
        self.performanceAction.setData(PerformanceData)
        self.recordAction = QAction("录制回放")
        self.recordAction.setData(recordData)
        self.uvc_clientAction = QAction("帧间隔测试")
        self.uvc_clientAction.setData(uvc_clientData)
        self.Repeat_FrameDataAction = QAction("重复帧测试")
        self.Repeat_FrameDataAction.setData(Repeat_FrameData)
        self.Exception_FrameDataAction = QAction("异常帧帧检测")
        self.Exception_FrameDataAction.setData(Exception_FrameData)


        self.testActions = []
        self.testActions.append(self.featureAction)
        self.testActions.append(self.performanceAction)
        self.testActions.append(self.recordAction)
        self.testActions.append(self.uvc_clientAction)
        self.testActions.append(self.Repeat_FrameDataAction)
        self.testActions.append(self.Exception_FrameDataAction)

        self.testMenu.addActions(self.testActions)

        self.configActions = []
        self.suitConfig = QAction("用例导入")
        self.suitConfig.triggered.connect(self.openFile)
       
        self.configActions.append(self.suitConfig)
        self.configMenu.addActions(self.configActions)

        # 用例管理界面
        self.suitManageAction = QAction("用例管理")
        self.suitManageAction.setData(SuitConfigData)
        self.configActions.append(self.suitManageAction)
        self.configMenu.addAction(self.suitManageAction)

    

    def openFile(self):
        self.textEdit = QtWidgets.QTextEdit()
        # 获取当前目录
        curPath = QDir.currentPath()
        fileName, filetype = QFileDialog.getOpenFileName(self, "选取文件",curPath, "Yaml Files (*.yaml)")
        suiteConfigData = SuiteConfigData()
        suiteConfigData.readSuiteConfigData(fileName)
        # 将文件内容转换为str 显示在textEdit中
        data= str(suiteConfigData.suiteCase)
        self.textEdit.setText(data)
        testCaseLayout=QHBoxLayout()
        testData=suiteConfigData.suiteCase
        if testData.get("cases"):
            for case in testData.get("cases"):
                print("case--->>>",case)
                self.addTestCase(case)
        print("文件类型：",type(suiteConfigData.suiteCase))
        print(fileName, filetype)
        print("文件内容类型：", type(data))
        self.textEdit.setPlainText(data)
        # # 最大化显示
        self.textEdit.showMaximized()
        # # 显示文件名
        self.setWindowTitle(fileName)
        return data
       # 将文件内容读取出来，然后显示在textEdit中

   

   