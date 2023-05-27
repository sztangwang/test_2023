import cv2
import time
from win32 import win32gui, win32print
from win32.lib import win32con
from PyQt5.QtGui import  QTransform
from PyQt5 import QtCore, QtGui
from PyQt5.QtWidgets import *
from ui.test.record.Util import SopThread
from ui.test.record import Configs
from ui.test.record.Util import TFile
from ui.test.record.Util import TAdb
from ui.test.record import scrcpy



class ScrcpyView(QWidget):
    console_signal = QtCore.pyqtSignal(str, str)
    select_insert_table_signal = QtCore.pyqtSignal(list)

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.mainwindow = parent
        self.setMouseTracking(True)
        self.installEventFilter(self)
        self.scrcpy_layout = QVBoxLayout()
        #self.scrcpy_layout
        self.label_show_view = QLabel()

        self.scrcpy_layout.addWidget(self.label_show_view)
        self.setLayout(self.scrcpy_layout)
        hDC = win32gui.GetDC(0)
        self.screen_width = win32print.GetDeviceCaps(hDC, win32con.DESKTOPHORZRES)
        self.set_gui()
        
    def set_gui(self):
        if TFile.get_config_value("is_image_view") == "adb":
            self.width_1080 = 480
            self.height_1080 = 800
        else:
            self.width_1080 = 800
            self.height_1080 = 480

        self.label_width = 460
        self.label_height = 800
        self.x_scale = 0.68 / 1.5  
        self.y_scale = 0.55 / 1.34
        self.screens = (int(self.width_1080), int(self.height_1080))
        self.label_show_view.setFixedSize(int(self.label_width), int(self.label_height))

    def mousePressEvent(self, event):
        if not Configs.is_image_show:
            return
        self.sx = int(event.x() / self.x_scale)
        self.sy = int(event.y() / self.y_scale)
    
    def mouseReleaseEvent(self, event):
        if not Configs.is_image_show:
            return
        print(event.x())
        print(event.y())
        self.ex = int(event.x() / self.x_scale)
        self.ey = int(event.y() / self.y_scale)

        if not TFile.get_config_value("CurrentDevice"):
            self.console_signal.emit('未选择设备', 'red')
            return

        if abs(self.ex - self.sx) > 10 or abs(self.ey - self.sy) > 10:
            TAdb.swipe(self.sx, self.sy, self.ex, self.ey)

            buttonItems = ['Adb滑动坐标',"无", "%s,%s，%s，%s"%(self.sx, self.sy, self.ex, self.ey),"无", '2', '1',"stop,continue"]
            self.console_signal.emit('Adb滑动坐标:%s,%s,%s,%s' % (self.sx, self.sy, self.ex, self.ey), 'lime')
        else:
            TAdb.click(self.sx, self.sy)
            buttonItems = ['Adb点击坐标',"无", "%s,%s"%(self.sx, self.sy), "无",'2', '1',"stop,continue"]
            self.console_signal.emit('Adb点击坐标:%s,%s' % (self.sx, self.sy), 'lime')

        if self.mainwindow.ToolBarView.recordMode_button.text() == '开启录制模式':
            return
        print(buttonItems)
      
        self.select_insert_table_signal.emit(buttonItems)
        

    def open_camera_view(self):
        camera_index = TFile.get_config_value("camera_name")[0]
        self.cap = cv2.VideoCapture(int(camera_index))
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH,5000)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT,5000)
        self.timer_camera = QtCore.QTimer()
        if not self.timer_camera.isActive():
            self.timer_camera.start(5)
        else:
            self.timer_camera.stop()
            self.cap.release()
            self.label_show_view.clear()
        self.timer_camera.timeout.connect(self.on_camera_frame)

    def open_adb_view(self):
        CurrentDevice = TFile.get_config_value("CurrentDevice")
        if not CurrentDevice:
            self.console_signal.emit('打开adb预览失败', 'Red')
            return
        if not TAdb.get_device_status(CurrentDevice):
            return

        self.client = scrcpy.Client(
            device=CurrentDevice, bitrate=1000000000
        )
        self.client.start(True)
        time.sleep(0.2)
        self.timer_adb = QtCore.QTimer()
        if not self.timer_adb.isActive():
            self.timer_adb.start(5)
        else:
            self.timer_adb.stop()
            self.cap.release()
            self.label_show_view.clear()
        self.timer_adb.timeout.connect(self.on_adb_frame)
        
 
    def open_view_connect(self):
        self.set_gui()
        Configs.is_image_show = True
        if TFile.get_config_value("is_image_view") in "card":
            self.open_camera_view()
        else:
            self.open_adb_view()



    def stop_camera(self):
        """ 停止相机服务 """
        self.cap.release()
        self.timer_camera.stop()

                
    def on_camera_frame(self):
        """ 相机图获取 """
        flag, frame = self.cap.read()
        if frame is None or not Configs.is_image_show:
            self.stop_camera()
            return
        self.image_view(frame)
        

    def on_adb_frame(self):
        """ adb 图获取 """
        if not Configs.is_image_show or not self.client.alive:
            print('adb图显示关闭')
            self.client.stop()
            self.timer_adb.stop()
            if self.client.alive:
                SopThread.stop_thread(self.client)
            self.label_show_view.clear()
            return
    
        self.image_view(self.client.last_frame)
            

    def image_view(self,frame):
        """ 图片显示 """
        if frame is not None:
            image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            if TFile.is_screenshot:
                cv2.imwrite(TFile.is_screenshot, frame)
                self.console_signal.emit('截图成功:%s' % TFile.is_screenshot, 'lime')
                if TFile.is_screenshot.count("Log\\base"):
                    cv2.namedWindow('截图显示', cv2.WINDOW_NORMAL) 
                    cv2.resizeWindow('截图显示', self.screens)
                    cv2.imshow('截图显示',frame)
                    cv2.waitKey(0)
                TFile.is_screenshot = ""

            image = cv2.resize(image, self.screens)
            showImage = QtGui.QImage(image.data, image.shape[1], image.shape[0], QtGui.QImage.Format_RGB888)
            pixmap = QtGui.QPixmap.fromImage(showImage)
            pixmap_rotated = pixmap.transformed(QTransform().rotate(Configs.revolve),QtCore.Qt.SmoothTransformation)
            self.label_show_view.setPixmap(pixmap_rotated)

            
