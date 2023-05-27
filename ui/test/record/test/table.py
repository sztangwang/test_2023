import sys
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5 import QtGui, QtCore
from PyQt5.QtSql import *
# import psycopg2

# 表头字段，全局变量
header_field = ['全选', '课程编号', '课程名称', '教师工号', '教师姓名', '教师职称', '授课时间', '授课地点']
# 用来装行表头所有复选框 全局变量
all_header_combobox = []

class CheckBoxHeader(QHeaderView):
    """自定义表头类"""

    # 自定义 复选框全选信号
    select_all_clicked = pyqtSignal(bool)
    # 这4个变量控制列头复选框的样式，位置以及大小
    _x_offset = 3
    _y_offset = 0
    _width = 20
    _height = 20

    def __init__(self, orientation=Qt.Horizontal, parent=None):
        super(CheckBoxHeader, self).__init__(orientation, parent)
        self.isOn = False

    def paintSection(self, painter, rect, logicalIndex):
        painter.save()
        super(CheckBoxHeader, self).paintSection(painter, rect, logicalIndex)
        painter.restore()

        self._y_offset = int((rect.height() - self._width) / 2.)

        if logicalIndex == 0:
            option = QStyleOptionButton()
            option.rect = QRect(rect.x() + self._x_offset, rect.y() + self._y_offset, self._width, self._height)
            option.state = QStyle.State_Enabled | QStyle.State_Active
            if self.isOn:
                option.state |= QStyle.State_On
            else:
                option.state |= QStyle.State_Off
            self.style().drawControl(QStyle.CE_CheckBox, option, painter)


    def mousePressEvent(self, event):
        index = self.logicalIndexAt(event.pos())
        if 0 == index:
            x = self.sectionPosition(index)
            if x + self._x_offset < event.pos().x() < x + self._x_offset + self._width and self._y_offset < event.pos().y() < self._y_offset + self._height:
                if self.isOn:
                    self.isOn = False
                else:
                    self.isOn = True
                    # 当用户点击了行表头复选框，发射 自定义信号 select_all_clicked()
                self.select_all_clicked.emit(self.isOn)
                self.updateSection(0)
        if 1 == index:
            print("a")
        super(CheckBoxHeader, self).mousePressEvent(event)

    # 自定义信号 select_all_clicked 的槽方法
    def change_state(self, isOn):
        # 如果行表头复选框为勾选状态
        if isOn:
            # 将所有的复选框都设为勾选状态
            for i in all_header_combobox:
                i.setCheckState(Qt.Checked)
        else:
            for i in all_header_combobox:
                i.setCheckState(Qt.Unchecked)



class stu_personal_course(QWidget):
    def __init__(self):
        super(stu_personal_course, self).__init__()
        self.resize(1200, 900)
        palette1 = QtGui.QPalette()
        palette1.setColor(self.backgroundRole(), QColor(153, 217, 234))  # 背景颜色
        self.setPalette(palette1)
        self.setAutoFillBackground(True)
        self.setWindowTitle("学生选课系统-学生-个人选课")

        self.setupUi()

    def setupUi(self):
        self.setObjectName("Form")
        self.resize(1200, 900)
        #设置 个人选课框
        self.groupBox = QtWidgets.QGroupBox(self)
        self.groupBox.setGeometry(QtCore.QRect(10, 120, 1180, 770))
        font = QtGui.QFont()
        font.setFamily("Adobe Arabic")
        font.setPointSize(11)
        font.setBold(True)
        font.setWeight(75)
        self.groupBox.setFont(font)
        self.groupBox.setObjectName("gerenxuankeliebiao")
        #设置 选课显示表
        self.tableWidget = QtWidgets.QTableWidget(self.groupBox)
        self.tableWidget.setGeometry(QtCore.QRect(10, 115, 1160, 645))
        self.tableWidget.setObjectName("tableWidget")

        self.tableWidget.setSelectionBehavior(QAbstractItemView.SelectRows)  # 设置表格的选取方式是行选取
        self.tableWidget.setSelectionMode(QAbstractItemView.SingleSelection)  # 设置选取方式为单个选取
        self.tableWidget.setColumnCount(8)
        self.tableWidget.setRowCount(20)
        self.tableWidget.setHorizontalHeaderLabels(["课程编号", "课程名称", "教师工号", "教师姓名", "教师职称", "授课时间", "授课地点"])  # 设置行表头
        self.tableWidget.setAlternatingRowColors(True)
        self.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tableWidget.horizontalHeader().setSectionResizeMode(0, QHeaderView.Interactive)
        self.setTableHeaderField()  # 设置表格行表头字段

        QtCore.QMetaObject.connectSlotsByName(self)
        
#START OF MY SECOND EDIT: search in your list of check boxes called all_header_combobx
    def pushButton_clicked(self):
        checked = []
        for num,box in enumerate(all_header_combobox):
            if box.isChecked():
                checked += [num+1]
        print(checked)  #this for print in the console a list with the numbers
#END OF MY SECOND EDIT

    def setTableHeaderField(self):

        self.tableWidget.setColumnCount(len(header_field))   # 设置列数
        for i in range(20):
            header_item = QTableWidgetItem(20)

            checkbox = QCheckBox()
            # 将所有的复选框都添加到 全局变量 all_header_combobox 中
            all_header_combobox.append(checkbox)
            # 为每一行添加复选框
            self.tableWidget.setCellWidget(i, 0, checkbox)

        header = CheckBoxHeader()               # 实例化自定义表头
        self.tableWidget.setHorizontalHeader(header)            # 设置表头
        self.tableWidget.setHorizontalHeaderLabels(header_field)        # 设置行表头字段
        self.tableWidget.setColumnWidth(0, 100)       # 设置第0列宽度
        header.select_all_clicked.connect(header.change_state)        # 行表头复选框单击信号与槽






if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = stu_personal_course()
    window.show()
    sys.exit(app.exec_())