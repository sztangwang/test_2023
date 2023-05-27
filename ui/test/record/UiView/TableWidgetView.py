from PyQt5 import QtCore
from ui.test.record.Util import TFile
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem, QAbstractItemView
from PyQt5.QtGui import QDropEvent


class TableWidgetView(QTableWidget):
    console_signal = QtCore.pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.mainwindow = parent

       
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Fixed)
        self.setRowCount(100)
        self.setColumnCount(7)
        self.setAcceptDrops(True)  # 开启接受拖入
        self.setDragEnabled(True)  # 开启拖拽
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setDragDropMode(QAbstractItemView.InternalMove)
        self.setHorizontalHeaderLabels(['事件名称', "类型",'事件内容', "对比值",'时间秒', '次数',"异常"])

        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)  # 自适应表格宽度
        self.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)  # 自适应表格高度

        self.horizontalHeader().setSectionResizeMode(0, QHeaderView.Interactive)
        self.horizontalHeader().setSectionResizeMode(1, QHeaderView.Interactive)
        self.horizontalHeader().setSectionResizeMode(6, QHeaderView.Interactive)

        self.setContextMenuPolicy(Qt.CustomContextMenu)  # 允许右键产生子菜单
        self.customContextMenuRequested.connect(self.tableWidget_menu)  # 右键菜单

        try:
            item = self.mainwindow.FileTreeView.currentItem().text()  # 获取文件列表选择文件名称
        except:
            return
        json_path = TFile.get_record_path()+item
        json_list = TFile.get_json_list(json_path)
        if not json_list:
            self.console_signal.emit('文件无数据:%s' % item)
            return
   
        for x , value in enumerate (json_list.values()):
            self.table_write(x, 0, value['name'])
            self.table_write(x, 1, value['types'])
            self.table_write(x, 2, value['content'])
            self.table_write(x, 3, value['value'])
            self.table_write(x, 4, value['sleep'])
            self.table_write(x, 5, value['num'])
            self.table_write(x, 6, value['exception'])

        
     

    def table_write(self,x, y, items):
        if y == 1 or y == 6:
            item_list = items.split(',')
            self.set_ComboBox_value(item_list,x,y)
        else:
            newItem = QTableWidgetItem(str(items))
            newItem.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
            self.setItem(x, y, newItem)
        self.selectColumn(1)
        self.set_scrollToItem(x)

    def set_scrollToItem(self,rows):
        """ 自动滚动 """
        self.scrollToItem(self.selectRow(rows),QAbstractItemView.PositionAtCenter)


    def keyPressEvent(self, event):
        if event.key() == 16777223:  # 快捷键delete键
            self.delete_item()


    def tableWidget_menu(self, pos):
        menu = QMenu()
        item2 = menu.addAction(u"Top")
        item3 = menu.addAction(u"Bottom")
        item1 = menu.addAction(u"Delete")
        item4 = menu.addAction(u"Delete all")
        try:
            action = menu.exec_(self.mapToGlobal(pos))
        except:
            return
        if action == item1:
            self.delete_item()
        if action == item2:
            self.top_item()
        if action == item3:
            self.bottom_item()
        if action == item4:
            self.delete_all_item()

    def bottom_item(self):
        """ 置底 """
        for i in self.selectedItems():
            i.row(), i.column(), i.text()
        type_list,exception_list = self.get_ComboBox_value(i.row())
        count = self.get_row_count()
        self.set_selected_to_row(count)
        self.set_ComboBox_value(type_list,count,1)
        self.set_ComboBox_value(exception_list,count,6)
        self.delete_item()
        self.scrollToItem(self.selectRow(j - 1), QAbstractItemView.PositionAtCenter)  # 自动滚动
        TFile.set_json_record(self.mainwindow.FileTreeView.currentItem().text(), self.get_all_item_dic(),is_clean=True)

    def top_item(self):
        """ 置顶 """
        for i in self.selectedItems():
            i.row(), i.column(), i.text()
        type_list,exception_list = self.get_ComboBox_value(i.row())
        self.insertRow(0)  # 插入到第一行
        self.set_selected_to_row(0)
        self.set_ComboBox_value(type_list,0,1)
        self.set_ComboBox_value(exception_list,0,6)
        self.delete_item()
        self.scrollToItem(self.selectRow(0), QAbstractItemView.PositionAtCenter)
        TFile.set_json_record(self.mainwindow.FileTreeView.currentItem().text(), self.get_all_item_dic(),is_clean=True)
    
    def get_row_count(self):
        row = self.rowCount()
        for count in range(0, row):
            items = self.item(count, 0)
            if items is None:
                return count

    def set_selected_to_row(self,row):
        """ 设置选中行到指定行 """
        y = 0
        for c, data in enumerate(self.get_selectedItems()):
            data.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
            if c == 1 or c == 6:   # 
                y = y + 1
            self.setItem(row, y, data)
            y = y + 1

    def get_selectedItems(self):
        """ 获取选中的数据 """
        selectedItemsList = []
        contents = self.selectedItems()
        for c, data in enumerate(contents):
            contents = data.text()
            newItem = QTableWidgetItem(contents)
            selectedItemsList.append(newItem)
        return selectedItemsList

    def get_all_item_dic(self):
        """ 获取页面全部数据字典格式 """
        conten_dic = {}
        for j in range(0, self.rowCount()):
            buttonItems = []
            for i in range(0, 7):
                if not self.item(j, i) and i !=1 and i !=6:
                    break
                elif i == 1 or i == 6:  # 添加下拉框数据
                    text_list = []
                    for count in range(self.cellWidget(j,i).count()):
                        text_list.append(self.cellWidget(j,i).itemText(count))
                    currentText = self.cellWidget(j,i).currentText()
                    text_list.remove(currentText) # 移除选中的名称
                    text_list.insert(0,currentText) # 插入到数组第一个元素
                    text = ','.join(text_list)
                elif not self.item(j, i):
                    break
                elif self.item(j, i):   # 添加普遍数据
                    text =  self.item(j, i).text()
                
                buttonItems.append(text)
            if buttonItems:
                title = str(TFile.get_datetime(format_str="%f"))+str(j)
                print(buttonItems)
                conten_dic.update({str(title):{'name':buttonItems[0],"types":buttonItems[1],
                                    "content":buttonItems[2],"value":buttonItems[3],
                                    "sleep":buttonItems[4],"num":buttonItems[5],
                                    "exception":buttonItems[6]}})
        return conten_dic
        

    def delete_item(self):
        index_list = []
        try:
            for model_index in self.selectionModel().selectedRows():
                index = QtCore.QPersistentModelIndex(model_index)
                index_list.append(index)
            for index in index_list:
                self.removeRow(index.row())
            file_name = self.mainwindow.FileTreeView.currentItem().text()
            conten_dic = self.get_all_item_dic()
            TFile.set_json_record(file_name, conten_dic,is_clean=True)

        except:
            self.console_signal.emit('删除异常', 'red')

    def delete_all_item(self):
        self.clearContents()
        file_name = self.mainwindow.FileTreeView.currentItem().text()
        file_path = TFile.get_record_path()+file_name
        with open(file_path, 'wb+') as f:
            f.close()
        self.console_signal.emit('清空脚本文件:%s' % file_path, 'red')

    def set_ComboBox_value(self,item_list,x,y):
        """ 设置下拉框数据 """
        self.ComboBox = QComboBox()
        self.ComboBox.addItems(item_list)
        self.ComboBox.setStyleSheet('QComboBox{margin:3px};')
        self.setCellWidget(x, y, self.ComboBox)


    def get_ComboBox_value(self,rows):
        """ 根据行获取下拉框数据 """
        type_list  = []
        for count in range(self.cellWidget(int(rows),1).count()):
            type_list.append(self.cellWidget(rows,1).itemText(count))

        exception_list  = []
        for count in range(self.cellWidget(rows,6).count()):
            exception_list.append(self.cellWidget(rows,6).itemText(count))
        return type_list,exception_list
        


    def dropEvent(self, event: QDropEvent):
        """ 拖动事件 """
    
        if not event.isAccepted() and event.source() == self:
            drop_row = self.drop_on(event)
            rows = sorted(set(item.row() for item in self.selectedItems()))
            type_list,exception_list = self.get_ComboBox_value(rows[0])
            rows_to_move = [
                [QTableWidgetItem(self.item(row_index, column_index)) for column_index in range(self.columnCount())]
                for row_index in rows]
            for row_index in reversed(rows):
                self.removeRow(row_index)
                if row_index < drop_row:
                    drop_row -= 1
            for row_index, data in enumerate(rows_to_move):
                row_index += drop_row
                self.insertRow(row_index)
                for column_index, column_data in enumerate(data):
                    self.setItem(row_index, column_index, column_data)
                    print(row_index, column_index, column_data)
            self.set_ComboBox_value(type_list,row_index,1)
            self.set_ComboBox_value(exception_list,row_index,6)
            event.accept()
            

            TFile.set_json_record(self.mainwindow.FileTreeView.currentItem().text(), self.get_all_item_dic(),is_clean=True)
        super().dropEvent(event)
      
    def drop_on(self, event):
        try:
            index = self.indexAt(event.pos())
            if not index.isValid():
                return self.rowCount()
            return index.row() + 1 if self.is_below(event.pos(), index) else index.row()
        except:
            print('拖动异常2')

    def is_below(self, pos, index):
        try:
            rect = self.visualRect(index)
            margin = 2
            if pos.y() - rect.top() < margin:
                return False
            elif rect.bottom() - pos.y() < margin:
                return True
            return rect.contains(pos, True) and not (
                    int(self.model().flags(index)) & Qt.ItemIsDropEnabled) and pos.y() >= rect.center().y()
        except:
            print('拖动异常3')

    def mouseReleaseEvent(self, event) -> None:
        TFile.set_json_record(self.mainwindow.FileTreeView.currentItem().text(), self.get_all_item_dic(),is_clean=True)


    def select_insert(self,buttonItems):
        select_rows = 0
        if len(self.selectedItems()) == 0:
            row = self.rowCount()  # 获取总共行数
            for j in range(0, row):
                items = self.item(j, 0)
                if items is None:
                    for i in range(0, len(buttonItems)):
                        self.table_write(j, i, buttonItems[i])
                    self.scrollToItem(self.selectRow(j),QAbstractItemView.PositionAtCenter)  # 自动滚动
                    break
        else:
            select_rows = (sorted(set(item.row() for item in self.selectedItems())))[0]
            self.insertRow(select_rows + 1)
            for i in range(0, len(buttonItems)):
                self.table_write(select_rows + 1, i, buttonItems[i])
        file_name = self.mainwindow.FileTreeView.currentItem().text()  #获取选择脚本文件的名称
        title = str(TFile.get_datetime())
        add_content = {str(title):{'name':buttonItems[0],"types":buttonItems[1],
                                   "content":buttonItems[2],"value":buttonItems[3],
                                   "sleep":buttonItems[4],"num":buttonItems[5],
                                   "exception":buttonItems[6]}}
        TFile.set_json_record(file_name, add_content)

       
 

    
