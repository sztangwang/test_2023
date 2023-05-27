# encoding: utf-8
import os
import random
import re
import sys
import cv2
import cgitb
import Configs
from Util import TFile
from PyQt5 import QtWidgets, QtGui
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from runTest.runThread import runThread
from UiView.StatusBarView import StatusBarView
from UiView.FileTreeView import FileTreeView
from UiView.ButtonEventView import ButtonEventView
from menubar.menuBarView import menuBarView
from UiView.RunExceptImageView import RunExceptImageView
from UiView.tableWidget import TableWidgetsView
from UiView.ToolBarView import ToolBarView
from UiView.ScrcpyView import ScrcpyView


cgitb.enable(format='text')

class main(QMainWindow):
    def __init__(self, parent=None):
        super(main, self).__init__(parent)
        self.statusBar().showMessage("正在检测计算机网络...",0)
        self.combox = locals()

        main_window_width = int(TFile.get_config_value('main_window_width'))
        main_window_height = int(TFile.get_config_value('main_window_height'))
        self.setGeometry(50, 50, main_window_width, main_window_height)
        self.status_bar_view = StatusBarView(self)  # 底部状态栏
        self.ToolBarView = ToolBarView(self)  # 工具栏
        self.menuView = menuBarView(self)  # 菜单栏

        tree_lable = QLabel('脚本区域')
        self.FileTreeView = FileTreeView(self)
        self.dock_file = QDockWidget(self)
        self.dock_file.setWidget(self.FileTreeView)
        self.dock_file.setTitleBarWidget(tree_lable)

        button = QLabel('按键区域')
        self.ButtonEventView = ButtonEventView(self)  # 按钮
        self.dock_buttonevent = QDockWidget(self)
        self.dock_buttonevent.setWidget(self.ButtonEventView)
        self.dock_buttonevent.setTitleBarWidget(button)

        table_label = QLabel('步骤展示区域')
        self.TableWidgetView = TableWidgetsView(self)
        self.dock_step = QDockWidget(self)
        self.dock_step.setTitleBarWidget(table_label)
        self.dock_step.setWidget(self.TableWidgetView)
     
        console_label = QLabel('控制台显示')
        self.Console = QtWidgets.QTextEdit()
        self.Console.document().setMaximumBlockCount(2000)  # 限制控制台显示行数
        self.dock_console = QDockWidget(self)
        self.dock_console.setWidget(self.Console)
        self.dock_console.setTitleBarWidget(console_label)
        self.Console.setFocusPolicy(Qt.NoFocus)

    
        self.scrcpyview = ScrcpyView(self)
        self.Scrcpy_label = QLabel('画面预览')
        self.Scrcpy_label.setStyleSheet("QLabel{border: 1px solid #74787c;border-width: 1px 1px 1px 1px;}")
        self.dock_scrcpyview = QDockWidget(self)
        self.dock_scrcpyview.setWidget(self.scrcpyview)
        self.dock_scrcpyview.setTitleBarWidget(self.Scrcpy_label)
        self.setMouseTracking(True)


        # 布局排序
        self.addDockWidget(Qt.LeftDockWidgetArea, self.dock_file)
        self.splitDockWidget(self.dock_file, self.dock_scrcpyview, Qt.Horizontal)
        self.splitDockWidget(self.dock_scrcpyview, self.dock_step, Qt.Horizontal)
        self.splitDockWidget(self.dock_step, self.dock_buttonevent, Qt.Vertical)
        self.splitDockWidget(self.dock_buttonevent, self.dock_console, Qt.Vertical)
        
        # 运行线程创建
        self.run_thread = runThread(self)
        self.setWindowTitle("TEST for TANGWANG V%s     " % 1.0)
        self.RunExceptImageView = RunExceptImageView(self)
        self.init_connect()

    def init_connect(self):
        # 线程信号槽
        self.run_thread.console_signal.connect(self.set_signal_consoleout)
        self.run_thread.except_image_signal.connect(self.set_signal_except_image)
        self.run_thread.progress_stype_signal.connect(self.set_signal_progress_stype)
        self.run_thread.num_signal.connect(self.set_signal_num)
        self.run_thread.scrollToItem_signal.connect(self.set_signal_scrollToItem)

        # 状态栏信号槽
        self.status_bar_view.console_signal.connect(self.set_signal_consoleout)

        # 脚本信号槽
        self.FileTreeView.console_signal.connect(self.set_signal_consoleout)
        self.FileTreeView.table_write_signal.connect(self.set_signal_table_write_connect)

        # 按键信号槽
        self.ButtonEventView.console_signal.connect(self.set_signal_consoleout)
       
        self.ButtonEventView.select_insert_table_signal.connect(self.set_signal_select_insert_table_connect)

        # 画面显示信号槽
        self.scrcpyview.console_signal.connect(self.set_signal_consoleout)
        self.scrcpyview.select_insert_table_signal.connect(self.set_signal_select_insert_table_connect)

        self.menuView.console_signal.connect(self.set_signal_consoleout)
        self.ToolBarView.console_signal.connect(self.set_signal_consoleout)

        self.menuView.select_insert_table_signal.connect(self.set_signal_select_insert_table_connect)



    def set_signal_except_image(self, image_list):
        """图像对比异常展示界面信号"""
        # #if 
        # self.label_picture = QtWidgets.QLabel()
        # self.label_picture2 = QtWidgets.QLabel()
        # try:
            
        #     picture1 = cv2.imread(image_list[0])
        #     picture1 = cv2.cvtColor(picture1, cv2.COLOR_BGR2RGB)
        #     picture1 = cv2.resize(picture1,(0,0),fx = 0.7,fy = 0.7)  
        #     self.showImage = QtGui.QImage(picture1.data, picture1.shape[1], picture1.shape[0], QtGui.QImage.Format_RGB888)
            
        #     self.RunExceptImageView.label_picture.setPixmap(QtGui.QPixmap.fromImage(self.showImage))
        self.RunExceptImageView.set_image_view(image_list)
        
        # except:
        #     print('弹出图像对比异常')

    def set_signal_progress_stype(self):
        """ 设置进度条信号 """
        index = random.randint(0, 100)
        self.status_bar_view.progress.setValue(index)

    def set_signal_scrollToItem(self,row):
        """ 设置滚动信号 """
        self.TableWidgetView.scrollToItem(self.TableWidgetView.selectRow(row), QAbstractItemView.PositionAtCenter)  # 自动滚动

    def set_signal_num(self):
        """ 设置运行次数信号 """
        self.status_bar_view.set_num()
    

    def set_signal_consoleout(self, text, colour):
        """控制台打印信号"""

        try:
            text = "{}-->{}".format(TFile.get_datetime('%m/%d/%H:%M:%S'),text)
            cursor = self.Console.textCursor()
            cursor.movePosition(QtGui.QTextCursor.End)
            self.Console.append('<font size=3 color=%s>%s </font>' % (colour, text))
            self.Console.setTextCursor(cursor)
            self.Console.ensureCursorVisible()
            filename = str('%s/control_Log_%s.txt' % (TFile.LOG_PATH,TFile.get_datetime('%Y%m%d')))
            with open(filename, 'a') as f:
                f.write(text + '\n')
        except:
            print('写入控制台日志异常，可能是硬盘已存储满')

     

    def set_signal_table_write_connect(self,x, y, items):
        """脚本写入表格信号"""
        
        self.TableWidgetView.table_write(x, y, items)

    def set_signal_select_insert_table_connect(self, buttonItems):
        """ 选择行插入表格 """
     

    


    def closeEvent(self, event):
        """关闭窗口时调用"""
        event.accept()
        os._exit(0)

    def resizeEvent(self, event):
        """获取窗口缩放事件，记录窗口大小"""
        w = event.size().width()
        h = event.size().height()
        TFile.set_config_file(w, 'main_window_width')
        TFile.set_config_file(h, 'main_window_height')

    def get_screen(self):
        """获取屏幕中心点坐标"""
    
        screen = QDesktopWidget().screenGeometry()
        Configs.screen_width = screen.width()
        Configs.screen_height = screen.height()
        screen_width = int((screen.width()) / 4)
        screen_height = int((screen.height()) / 4)
        TFile.set_config_file(str(screen_width), 'screen_width')
        TFile.set_config_file(str(screen_height), 'screen_height')


if __name__ == "__main__":
    app = QApplication(sys.argv)
    workpath = os.path.dirname(sys.argv[0])
    os.chdir(workpath)  # 指定py文件执行路径为当前工作路径
    app.setStyleSheet(open('./Config/styleSheet.qss', encoding='utf-8').read())
    window = main()
    window.get_screen()
    window.show()
    sys.exit(app.exec_())
