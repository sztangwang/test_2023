import re
import cv2
from PyQt5.QtCore import Qt
from PyQt5 import QtGui, QtWidgets, QtCore
from ui.test.record.Util import TFile
from ui.test.record.Util import TPicture
from PyQt5.QtWidgets import QWidget, QGridLayout, QPushButton

class RunExceptImageView(QWidget):

    def __init__(self, mainwindow):
        super().__init__()
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        self.mainwindow = mainwindow
        self.setGeometry(300, 300, 500, 350)
        self.setWindowTitle("异常提示")
        self.mainLayout = QGridLayout()
        self.setLayout(self.mainLayout)

    def set_image_view(self,image_list):
        """ 设置多张图片或者一张图片展示 """
        
        self.image_list = image_list
        if isinstance(self.image_list, str):
            label = QtWidgets.QLabel(self.image_list)
            label.setStyleSheet("color: red;font-size:50px;}")
            self.mainLayout.addWidget(label, 0, 0,alignment=Qt.AlignHCenter)
            self.show()
            return


        self.label_picture = locals()
        for i,image in enumerate(image_list):
            self.label_picture[str(i)] = QtWidgets.QLabel()
            image = cv2.imread(image)
            self.set_lable_view(image,self.label_picture[str(i)])
            self.mainLayout.addWidget(self.label_picture[str(i)], 0, i)
        if len(self.image_list) > 0:
            self.view_not_alike = QPushButton('显示不同点')
            self.view_not_alike.setMaximumWidth(200)
            self.view_not_alike.clicked.connect(self.view_not_alike_connect)
        self.mainLayout.addWidget(self.view_not_alike, 1, 0)
        self.show()

    def set_lable_view(self,image,lable):
        lable.clear()
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        if image.shape[1] > 500:
            image = cv2.pyrDown(image)  
     
        showImage = QtGui.QImage(image.data, image.shape[1], image.shape[0], QtGui.QImage.Format_RGB888)
        lable.setPixmap(QtGui.QPixmap.fromImage(showImage))

    def view_not_alike_connect(self):
        """ 设置显示不同点 """
        if self.view_not_alike.text() == '取消显示':
            image1 = cv2.imread(self.image_list[0])
            image2 = cv2.imread(self.image_list[1])
            self.set_lable_view(image1,self.label_picture[str(0)])
            self.set_lable_view(image2,self.label_picture[str(1)])
            self.view_not_alike.setText("显示不同点")
        else:
            img1 , img2 = TPicture.set_opencv_contourArea(self.image_list[0],self.image_list[1])
            self.set_lable_view(img1,self.label_picture[str(0)])
            self.set_lable_view(img2,self.label_picture[str(1)])
            self.view_not_alike.setText("取消显示")



    def closeEvent(self, event):
        self.destroy()


   