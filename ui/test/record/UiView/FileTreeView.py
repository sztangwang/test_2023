import os
import re
from ui.test.record.Util import TFile
from PyQt5 import QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtGui import  QCursor
from PyQt5.QtWidgets import *


class tree_item(QTreeWidgetItem):
    def __init__(self, column, text):
        super().__init__()
        self.setText(column, text)


class FileTreeView(QListWidget):
    console_signal = QtCore.pyqtSignal(str, str)
    table_write_signal = QtCore.pyqtSignal(int, int,str)

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.record_file_list = TFile.get_record_file_list()
        self.mainwindow = parent
        self.record_path = TFile.get_record_path()
        
        self.InitUi()


    def InitUi(self):
        #self.setMinimumWidth(300)
        self.addItems(self.record_file_list)
        self.clicked.connect(self.tree_click_connect)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.contextMenu = QMenu(self)
        self.new_treefile = self.contextMenu.addAction(' New File... ')
        self.del_treefile = self.contextMenu.addAction(' Delete... ')
        self.rename_treefile = self.contextMenu.addAction(' Rename... ')
        self.delAll_treefile = self.contextMenu.addAction(' Delete All... ')

        self.customContextMenuRequested.connect(self.showContextMenu)
        self.new_treefile.triggered.connect(self.new_treefile_connect)
        self.del_treefile.triggered.connect(self.del_treefile_connect)
        self.rename_treefile.triggered.connect(self.rename_treefile_connect)
        self.delAll_treefile.triggered.connect(self.delAll_treefile_connect)

        treeFile_num = int(TFile.get_config_value('treeFile_item'))
        if self.count() != 0:
            if self.count() < treeFile_num+1:  # 如果总行数小于选择的行数，说明该行不存在，所以设置为0
                self.setCurrentRow(0)  # 设置列表默认选中行
            else:
                self.setCurrentRow(treeFile_num)  # 设置列表默认选中行


    def tree_click_connect(self, index):
        if self.mainwindow.ToolBarView.run_button.text() == '停止':
            self.console_signal.emit('运行测试过程中无法选择脚本操作！', 'red')
            return
        item = self.currentItem().text()  # 获得当前单击项
        TFile.set_config_file(self.currentIndex().row(),'treeFile_item')  # 获取当前选中行
        self.mainwindow.TableWidgetView.clearContents()
        self.console_signal.emit('选择文件:%s' % item, 'black')

        json_path = TFile.get_record_path()+item
        json_list = TFile.get_json_list(json_path)
        if not json_list:
            self.console_signal.emit('文件无数据:%s' % item, 'red')
            return
        
        for x , value in enumerate (json_list.values()):
            self.table_write_signal.emit(x, 0, value['name'])
            self.table_write_signal.emit(x, 1, value['types'])
            self.table_write_signal.emit(x, 2, value['content'])
            self.table_write_signal.emit(x, 3, value['value'])
            self.table_write_signal.emit(x, 4, str(value['sleep']))
            self.table_write_signal.emit(x, 5, str(value['num']))
            self.table_write_signal.emit(x, 6, value['exception'])

    def showContextMenu(self):
        # 如果有选中项，则显示显示菜单
        items = self.selectedIndexes()
        if items:
            self.contextMenu.show()
            self.contextMenu.exec_(QCursor.pos())  # 在鼠标位置显示

    def new_treefile_connect(self):
        self.mainwindow.menuView.FilesMenuBarView.new_file_connect()

    def del_treefile_connect(self):
        self.mainwindow.menuView.FilesMenuBarView.del_file_connect()

    def delAll_treefile_connect(self):
        for c in range(self.count()):
            self.mainwindow.menuView.FilesMenuBarView.del_file_connect()


    def rename_treefile_connect(self):
        note = self.currentItem().text()
        srcFile = '%s%s' % (self.record_path,note)
     
        inputDialog = QInputDialog(self)
        inputDialog.resize(100,500)
        value, ok = inputDialog.getText(self, "Rename", '', QLineEdit.Normal, note)
        if ok:
            dstFile = '%s/%s' % (self.record_path,value)
            os.rename(srcFile, dstFile)
            self.removeItemWidget(self.takeItem(self.currentIndex().row()))
            self.addItems([value])
