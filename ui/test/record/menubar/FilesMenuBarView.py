import os
import time
from PyQt5 import QtCore
from ui.test.record import Configs
from ui.test.record.Util import TFile
from PyQt5.QtWidgets import QWidget, QAction



class FilesMenuBarView(QWidget):
    console_signal = QtCore.pyqtSignal(str)
    def __init__(self, mainwindow):
        super().__init__()
        self.mainwindow = mainwindow
         
        self.FileUi()

    def FileUi(self):
        self.file = self.mainwindow.menuBars.addMenu("  File  ")
        self.new_file = QAction('New File...', self)
        self.file.addAction(self.new_file)
        self.new_file.triggered.connect(self.new_file_connect)

        self.del_file = QAction('Del File...', self)
        self.file.addAction(self.del_file)
        self.del_file.triggered.connect(self.del_file_connect)

        self.cleanFile = QAction('Clean File...', self)
        self.file.addAction(self.cleanFile)
        self.cleanFile.triggered.connect(self.clean_file_connect)

        self.revolve = QAction('顺时针旋转90度', self)
        self.file.addAction(self.revolve)
        self.revolve.triggered.connect(self.revolve_connect)

        self.image_view = QAction('关闭/打开图像预览', self)
        self.file.addAction(self.image_view)
        self.image_view.triggered.connect(self.image_view_connect)

        self.exit = QAction('Exit', self)
        self.file.addAction(self.exit)
        self.exit.triggered.connect(self.exit_connect)

    def image_view_connect(self):
        """ 图像预览显示关闭"""
        if not Configs.is_image_show:
            self.mainwindow.ScrcpyView.open_view_connect()
        else:
            Configs.is_image_show = False
       


    def revolve_connect(self):
        """ 旋转90度"""
        Configs.revolve = Configs.revolve + 90


    def clean_file_connect(self):
        self.mainwindow.TableWidgetView.clearContents()
        script_file = TFile.get_config_value('script_file')
        open(TFile.get_record_path()+script_file, 'wb+')
        self.console_signal.emit('已清空脚本文件:%s' % script_file)

    def del_file_connect(self):
        try:
            select_file = self.mainwindow.FileTreeView.currentItem().text()
        except:
            return
        try:
            self.mainwindow.FileTreeView.removeItemWidget(
                self.mainwindow.FileTreeView.takeItem(self.mainwindow.FileTreeView.currentIndex().row()))
            TFile.remove_file(TFile.get_record_path() + select_file)
            self.console_signal.emit('删除文件:%s' % select_file)
            self.mainwindow.TableWidgetView.clearContents()
        except FileNotFoundError:
            self.console_signal.emit('删除文件失败:%s' % select_file)
        note = self.mainwindow.FileTreeView.currentItem()
        item = ''
        if not note is None:
            item = note.text()  # 获得当前单击项
        TFile.set_config_file(item, 'TreeFile')

    def new_file_connect(self):
        file_name = 'record_%s.json'% TFile.get_datetime(format_str="%m%d%H%M%S")
        TFile.set_new_file(TFile.get_record_path()+file_name)

        self.mainwindow.FileTreeView.addItems([file_name])
        TFile.set_config_file(file_name, 'TreeFile')
        self.console_signal.emit('新建文件：%s' % file_name,)
        self.mainwindow.FileTreeView.setCurrentRow(self.mainwindow.FileTreeView.count() - 1)  # 新建文件后选择最后一行
        self.mainwindow.TableWidgetView.clearContents()  # 新建完成后清除表格中的数据


    def exit_connect(self):
        self.mainwindow.destroy()
        os._exit(0)


      