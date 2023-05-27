import random
from PyQt5.QtCore import Qt
from PyQt5 import QtWidgets
from ui.test.record.UiView.ToolBarView import ToolBarView
from ui.test.record.UiView.FileTreeView import FileTreeView
from ui.test.record.UiView.ScrcpyView import ScrcpyView
from ui.test.record.UiView.ButtonEventView import ButtonEventView
from ui.test.record.UiView.TableWidgetView import TableWidgetView
from ui.test.record.UiView.ConsoleView import ConsoleView
from ui.test.record.UiView.RunExceptImageView import RunExceptImageView
from compoment.atx2agent.core.common.logs.log_uru import Logger
from ui.test.record.menubar.HelpView import HelpView
from ui.test.record.menubar.MenuToolsView import MenuToolsView
from ui.test.record.menubar.FilesMenuBarView import FilesMenuBarView
from ui.test.record.menubar.moreFeaturesView import moreFeaturesView
from ui.test.record.Util import TFile
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QSplitter, QTabWidget, QMenuBar
from ui.test.record.runTest.runThread import runThread

logger = Logger().get_logger

class record_main(QtWidgets.QWidget):
    def __init__(self, tuple_device=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tuple_device = tuple_device
        self.pool,self.adbConnectionDeviceList,self.runners= self.tuple_device
        self.initUI(self)

    def initUI(self, layout: QWidget):
        self.setWindowTitle('录制回放')
        #self.setFixedSize(1700,1000)
        main_window_width = int(TFile.get_config_value('main_window_width'))
        main_window_height = int(TFile.get_config_value('main_window_height'))
    

        self.setGeometry(50, 50, main_window_width, main_window_height)

        self.menuBars = QMenuBar()                      # 菜单栏
        self.FilesMenuBarView = FilesMenuBarView(self)
        self.moreFeaturesView = moreFeaturesView(self)
        self.MenuToolsView = MenuToolsView(self)
        self.help_view = HelpView(self)

        self.ToolBarView = ToolBarView(self)            # 工具栏

        self.tab_widget = QWidget()
        self.tab = TabWidget(self.tab_widget)

        self.FileTreeView = FileTreeView(self)          # 脚本栏
        self.ScrcpyView = ScrcpyView(self)              # 相机显示栏
        self.tab.addTab(self.FileTreeView, '脚本显示')
        self.tab.addTab(self.ScrcpyView, '画面预览')

        self.ButtonEventView = ButtonEventView(self)    # 按键栏
        self.TableWidgetView = TableWidgetView(self)    #表格显示栏
        self.ConsoleView = ConsoleView(self)            #输出显示栏

        self.top_QSplitter = QSplitter(Qt.Vertical)

        self.Splitter = QSplitter(Qt.Horizontal)
        self.right_layout = QSplitter(Qt.Vertical)
    
        self.top_QSplitter.addWidget(self.menuBars)
        self.top_QSplitter.addWidget(self.ToolBarView)

        self.right_layout.addWidget(self.TableWidgetView)
        self.right_layout.addWidget(self.ButtonEventView)
        self.right_layout.addWidget(self.ConsoleView)

        self.Splitter.addWidget(self.tab_widget)
        self.Splitter.addWidget(self.right_layout)
      

        Vertical = QSplitter(Qt.Vertical)
        Vertical.addWidget(self.top_QSplitter)
        Vertical.addWidget(self.Splitter)
       
        layout = QVBoxLayout()
        layout.addWidget(Vertical)
        self.setLayout(layout)
        self.run_thread = runThread(self)
        self.set_signal()
        

    def set_signal(self):
        self.ToolBarView.console_signal.connect(self.set_signal_consoleout)
        self.FileTreeView.console_signal.connect(self.set_signal_consoleout)
        self.ScrcpyView.console_signal.connect(self.set_signal_consoleout)
        self.ButtonEventView.console_signal.connect(self.set_signal_consoleout)
        self.TableWidgetView.console_signal.connect(self.set_signal_consoleout)
        self.ButtonEventView.select_insert_table_signal.connect(self.set_signal_insert_table_connect)
        self.ScrcpyView.select_insert_table_signal.connect(self.set_signal_insert_table_connect)
        self.run_thread.except_image_signal.connect(self.set_signal_except_image)
        self.run_thread.except_msg_signal.connect(self.set_sinal_except_msg)
        self.run_thread.num_signal.connect(self.set_signal_num)
        self.run_thread.scrollToItem_signal.connect(self.set_signal_scrollToItem)
        self.run_thread.console_signal.connect(self.set_signal_consoleout)

        self.moreFeaturesView.console_signal.connect(self.set_signal_consoleout)
        self.moreFeaturesView.select_insert_table_signal.connect(self.set_signal_insert_table_connect)
        self.FilesMenuBarView.console_signal.connect(self.set_signal_consoleout)

    def set_signal_consoleout(self, text):
        """ 打印"""
        self.ConsoleView.out_print(text)

    def set_signal_except_image(self, image_list):
        """图像对比异常展示界面信号"""
        self.RunExceptImageView = RunExceptImageView(self)
        self.RunExceptImageView.set_image_view(image_list)

    def set_signal_scrollToItem(self,row):
        """ 设置滚动信号 """
        self.TableWidgetView.set_scrollToItem(row)
    def set_signal_num(self):
        """ 设置运行次数信号 """
        self.ToolBarView.set_num()

    def set_signal_table_write_connect(self,x, y, items):
        """脚本写入表格信号"""
        self.TableWidgetView.table_write(x, y, items)

    def set_signal_insert_table_connect(self, buttonItems):
        """ 选择行插入表格 """
        self.TableWidgetView.select_insert(buttonItems)
  
    
    def set_sinal_except_msg(self,text):
        self.RunExceptImageView = RunExceptImageView(self)
        self.RunExceptImageView.set_image_view(text)

    def resizeEvent(self, event):
        """获取窗口缩放事件，记录窗口大小"""
        w = event.size().width()
        h = event.size().height()
        
        TFile.set_config_file(w, 'main_window_width')
        TFile.set_config_file(h, 'main_window_height')


class TabWidget(QTabWidget):
  def __init__(self, parent=None) -> None:
    super().__init__(parent)

  def remove_tab_handler(self):
    '''
    槽函数, 移除索引为0的选项卡
    '''
    super().removeTab(0)




