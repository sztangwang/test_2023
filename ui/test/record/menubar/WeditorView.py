import re
import time
from PyQt5 import QtCore, QtWebEngineWidgets
from ui.test.record import String
from PyQt5.QtWidgets import QWidget, QPushButton, QVBoxLayout,QLineEdit,QLabel,QHBoxLayout,QGridLayout,QComboBox

class WeditorView(QWidget):
    def __init__(self,select_insert_table_signal):
        super().__init__()
        self.select_insert_table_signal = select_insert_table_signal
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        #self.setGeometry(200, 400, 680, 150)
        self.setWindowTitle('Weditor')
        self.IntUi()

    def IntUi(self):
        types = ['找不到','找到']
        wl = QHBoxLayout(self)  # 全局布局

        self.Left_layout = QVBoxLayout()     # 左边布局
        self.Right_layout = QGridLayout()     # 右边布局

        self.WebEngineView = QtWebEngineWidgets.QWebEngineView()
        # self.WebEngineView.resize(900, 1280)
        self.WebEngineView.setMaximumWidth(800)
        self.WebEngineView.setMinimumHeight(720)
        line = QLineEdit()
        line.setMaximumHeight(5)
        line1 = QLineEdit()
        line1.setMaximumHeight(5)

        self.reload_button = QPushButton('刷新')

        self.text_edit = QLineEdit()
        self.text_button = QPushButton('文本点击')
        self.text_asser = QPushButton('文本断言')
        self.text_asser_type = QComboBox()
        self.text_asser_type.addItems(types)
        

        self.xpath_edit = QLineEdit()
        self.xpath_button = QPushButton('Xpath点击')
        self.xpath_asser = QPushButton('Xpath断言')
        self.xpath_asser_type = QComboBox()
        self.xpath_asser_type.addItems(types)

        self.resourceId_edit = QLineEdit()
        self.resourceId_button = QPushButton('resourceId点击')
        self.resourceId_asser = QPushButton('resourceId断言')
        self.resourceId_asser_type = QComboBox()
        self.resourceId_asser_type.addItems(types)
        self.text_resourceId = QPushButton('Text与resourceId点击')


        self.text_edit.setMinimumWidth(250)
        self.reload_button.clicked.connect(lambda: self.WebEngineView.reload()) 

        self.text_button.clicked.connect(lambda: self.event_connect(self.text_button.text(),self.text_edit.text())) 
        self.text_asser.clicked.connect(lambda: self.event_connect(self.text_asser.text(),self.text_edit.text(),
                                        types=String.find_type)) 

        self.xpath_button.clicked.connect(lambda: self.event_connect(self.xpath_button.text(),self.xpath_edit.text())) 
        self.xpath_asser.clicked.connect(lambda: self.event_connect(self.xpath_button.text(),self.xpath_edit.text(),
                                                                    types=String.find_type)) 

        self.resourceId_button.clicked.connect(lambda: self.event_connect(self.resourceId_button.text(),self.resourceId_edit.text()))
        self.resourceId_asser.clicked.connect(lambda: self.event_connect(self.resourceId_asser.text(),self.resourceId_edit.text(),
                                                                         types=String.find_type))
        self.text_resourceId.clicked.connect(lambda: self.event_connect(self.text_resourceId.text(),self.resourceId_edit.text()+','+
                                                                        self.text_edit.text()))

        #self.WebEngineView.resize(1000, 1280)
        self.WebEngineView.load(QtCore.QUrl('http://localhost:17310/'))
        #self.WebEngineView.setZoomFactor
        self.WebEngineView.loadFinished.connect(self.finished)
        self.WebEngineView.selectionChanged.connect(self.print)
        self.WebEngineView.setZoomFactor(1)
        #str = "$(\"#su\").submit();"
        #str = "$(\".form_group\").find(\"input\").val(\"333\");"
        

        self.Left_layout.addWidget(self.WebEngineView)
        self.Right_layout.addWidget(self.reload_button,0,0)

        self.Right_layout.addWidget(QLabel('Text'),1,0)
        self.Right_layout.addWidget(self.text_edit,1,1,1,4)
        self.Right_layout.addWidget(self.text_button,2,0)
        self.Right_layout.addWidget(self.text_asser,2,1)
        self.Right_layout.addWidget(QLabel('断言类型'),2,2)
        self.Right_layout.addWidget(self.text_asser_type,2,3)
        self.Right_layout.addWidget(line,3,0,1,4)
        
 
        self.Right_layout.addWidget(QLabel('Xpath'),4,0)
        self.Right_layout.addWidget(self.xpath_edit,4,1,1,4)
        self.Right_layout.addWidget(self.xpath_button,5,0)
        self.Right_layout.addWidget(self.xpath_asser,5,1)
        self.Right_layout.addWidget(QLabel('断言类型'),5,2)
        self.Right_layout.addWidget(self.xpath_asser_type,5,3)
        self.Right_layout.addWidget(line1,6,0,1,4)

        self.Right_layout.addWidget(QLabel('resourceId'),9,0)
        self.Right_layout.addWidget(self.resourceId_edit,9,1,1,4)
        self.Right_layout.addWidget(self.resourceId_button,10,0)
        self.Right_layout.addWidget(self.resourceId_asser,10,1)
        self.Right_layout.addWidget(QLabel('断言类型'),10,2)
        self.Right_layout.addWidget(self.resourceId_asser_type,10,3)
        self.Right_layout.addWidget(self.text_resourceId,11,0)
        
        self.Right_layout.setSpacing(0)
        
        wl.addLayout(self.Left_layout)
        wl.addLayout(self.Right_layout)
  

    def finished(self):
        self.setWindowTitle(self.WebEngineView.title())  # 更新視窗標題
        self.setWindowIcon(self.WebEngineView.icon())    # 更新視窗圖示
        time.sleep(0.1)
        self.remove_element()

    def remove_element(self):
        str = "document.getElementById(\"footer\").remove();"
        str1 = "[...document.getElementsByClassName(\"panel panel-default middle-panel\")].map(n => n && n.remove());"
        str2 = "[...document.getElementsByClassName(\"navbar-brand\")].map(n => n && n.remove());"
        #str3 = "document.getElementById(\"screen\").style.width=\"800px;\""
        str4 = "document.getElementById(\"right\").remove();"
        str5 = "document.getElementsByClassName(\"form-control\").value = 123;"
        self.WebEngineView.page().runJavaScript(str)
        self.WebEngineView.page().runJavaScript(str1)
        self.WebEngineView.page().runJavaScript(str2)
        self.WebEngineView.page().runJavaScript(str4)
        self.WebEngineView.page().runJavaScript(str5)
        #self.WebEngineView.page().runJavaScript(str3)
        


    def print(self):
        self.remove_element()
        text = self.WebEngineView.selectedText()
        self.xpath_edit.setText('')
        self.resourceId_edit.setText('')
        self.text_edit.setText('')

        if text.count('d.xpath') > 0:
            texts = ((re.findall(r'd.xpath\(\'(.+?)\'', text))[0])
            self.xpath_edit.setText(texts)

        if text.count('resourceId=') > 0:
            texts = ((re.findall(r'resourceId=\"(.+?)\"', text))[0])
            self.resourceId_edit.setText(texts)

        if text.count('text=') > 0:
            texts = ((re.findall(r'text=\"(.+?)\"', text))[0])
            self.text_edit.setText(texts)

    def event_connect(self,name,text,types='无',match_value='无'):
        if text:
            buttonItems = ['ui2_'+name,types ,text,match_value, '3', '1',String.Exception_List]
            self.select_insert_table_signal.emit(buttonItems)
     
        

       

    def cancel_connect(self):
        self.destroy()

