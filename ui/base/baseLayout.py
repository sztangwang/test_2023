
import os
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QHeaderView, QAction
from ui.base.infoLayout import infoLayout
from ui.base.toolLayout import toolLayout
from ui.base.bottomLayout import bottomLayout
from ui.base.menuBarLayout import menuBarLayout
from ui.base.consoleLayout import consoleLayout
from config.menuDataConfig import *
TEST_CASE_LIST =[]

class BaseLayout(QMainWindow):

    def initUi(self):
        self.mainMenu = self.menuBar()
        self.mainMenuLayout = menuBarLayout(self) # 顶部菜单栏

        #self.tool_bar = toolLayout(self)            # 工具栏

        self.bottomLayout = bottomLayout(self)      # 底部状态栏
        

        self.console_layout = consoleLayout(self)    # 控制台输出
        
        self.dock_console = QDockWidget(self)
        self.dock_console.setWindowTitle('Log输出区域')
        self.dock_console.setWidget(self.console_layout.widget)


        self.tableWidget = QtWidgets.QTableWidget() #设备列表区域
        self.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tableWidget.setRowCount(1)
        self.tableWidget.setLineWidth(0)
        self.dock_tableWidget = QDockWidget(self)
        self.dock_tableWidget.setWidget(self.tableWidget)
        self.dock_tableWidget.setWindowTitle('设备列表区域')
        
        self.infoLayout = infoLayout()              # 信息展示区域
        self.dock_infoLayout = QDockWidget(self)
        self.dock_infoLayout.setWidget(self.infoLayout)
        self.dock_infoLayout.setWindowTitle('信息展示区域')

         # 布局排序
        self.addDockWidget(Qt.LeftDockWidgetArea, self.dock_infoLayout)
        self.splitDockWidget(self.dock_infoLayout, self.dock_tableWidget, Qt.Horizontal)
        self.splitDockWidget(self.dock_tableWidget, self.dock_console, Qt.Vertical)
     

    
    def addTestCase(self,testCaseList:list):
        # 保存测试用例到全局变量中
        TEST_CASE_LIST.append(testCaseList)

    def closeEvent(self, event):
        """关闭窗口时调用"""
        event.accept()
        os._exit(0)




    


