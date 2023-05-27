
import os
import subprocess
import sys
import cv2
import time
import numpy
import datetime
from pathlib import Path
from queue import Queue
from threading import Thread
from ui.test.Exception_Frame import configs
from ui.test.uvc_test.log_uru import Logger

def get_project_path():
    return os.path.dirname(os.path.abspath(__file__))
sys.path.append(get_project_path())

logger = Logger().get_logger


STOP_THREAD = False

def compare(last_hash, current_hash):
    return last_hash == current_hash


def kill_pid():
    # 通过pid杀死进程
    subprocess.Popen("taskkill /F /T /PID " + str(os.getpid()), shell=True)

def second_to_time(second):
    m, s = divmod(second, 60)
    h, m = divmod(m, 60)
    return "%02d:%02d:%02d" % (h, m, s)


  


class UVCUtils:
    def __init__(self):
        self.stop = False
        self.cv2 = cv2

    def openUVC(self):
        if self.stop:
            self.stop = False
     
        self.capture = self.cv2.VideoCapture(configs.camera_index)
        assert self.capture.isOpened(), "Could not open video device"
        self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, configs.width)
        self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, configs.height)
        self.capture.set(5, configs.default_fps)
        if configs.types is not None:
            self.capture.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*configs.types))  # YUYV，MJPG，YV12
        width = self.capture.get(cv2.CAP_PROP_FRAME_WIDTH)
        height = self.capture.get(cv2.CAP_PROP_FRAME_HEIGHT)
        logger.debug("CAP_PROP_FOURCC:{}".format(self.capture.get(cv2.CAP_PROP_FOURCC)))
        logger.debug(f"Screen resolution :{width} * {height}")
        pos_frame = self.capture.get(cv2.CAP_PROP_POS_FRAMES)
        self.path = "%s/images/"%Path(__file__).resolve().parents[0]
        for i in os.listdir(self.path):
            c_path = os.path.join(self.path, i)
            os.remove(c_path)       # 删除所有图片
        start_time = time.time()
    
        while self.capture.isOpened():
            ret, self.frame = self.capture.read()
            if ret:
                current_time = time.time() - start_time
                if current_time > configs.run_time: # 判断是否大于设置的运行设置，大于则结束测试
                    self.capture.release()
                    break
                if STOP_THREAD:
                    self.stopUVC()
                #self.cv2.imwrite("%s/%s.png"%(path,i),frame)
                self.run_test()

                strs= "run_time: {}".format(round(current_time,1))+"Resolution:{}*{}".format(width, height)
                self.cv2.putText(self.frame,strs, (50, 50),cv2.FONT_HERSHEY_DUPLEX, 2, (0, 255, 255),1)
                self.cv2.imshow('webCam', self.frame)
                if self.cv2.waitKey(1) == ord('s'):
                    break

            else:
                self.capture.set(cv2.CAP_PROP_POS_FRAMES, pos_frame - 1)
                cv2.waitKey(1000)
                self.capture.open(0)
                continue
    

    def run_test(self):
        self.picture_status = self.get_picture_status() 
        if configs.black_test and self.picture_status == "BLACK":
            self.cv2_imwrite(self.frame)

        if configs.green_test and self.picture_status == "GREEN":
            self.cv2_imwrite(self.frame)
            
        #print(self.blurred_screen_test())
        # if configs.blurred_screen_test:
        
        # if configs.green_test:
        #print()
    def blurred_screen_test(self):
        img2gray = cv2.cvtColor(self.frame, cv2.COLOR_BGR2GRAY)  # 将图片压缩为单通道的灰度图
        # img_resize = cv2.resize(img2gray, (112, 112))  # 为方便与其他图片比较可以将图片resize到同一个大小
        score = cv2.Laplacian(img2gray, cv2.CV_64F).var()
        if score < 5:
            print(score)
        
    def cv2_imwrite(self,frame):
        times = datetime.datetime.now().strftime("%m%d%H_%M_%S_%f")
        file = "%s/%s.png"%(self.path,times)
        self.cv2.imwrite(file,frame)
        print(file + " ===  " + self.picture_status)



    def stopUVC(self):
        self.toc = time.perf_counter()  # 结束计时
        # 持续时间
  
        self.stop = True
        # 恢复self.sleep的值
        self.sleep = 1
        self.capture.release()
        self.cv2.destroyAllWindows()


    def get_picture_status(self,is_cut=True):
        if is_cut:
            img = self.frame[200:1100, 0:1200]
     
        (b, g, r) = cv2.split(img)
        b_avg, b_min, b_max, b_std = numpy.mean(b), numpy.min(b), numpy.max(b), numpy.std(b)
        g_avg, g_min, g_max, g_std = numpy.mean(g), numpy.min(g), numpy.max(g), numpy.std(g)
        r_avg, r_min, r_max, r_std = numpy.mean(r), numpy.min(r), numpy.max(r), numpy.std(r)

        # print(numpy.max([b_std, g_std, r_std]))
        # print(numpy.std([b_avg, g_avg, r_avg]))
        if b_min >= 64 and r_avg < (255-3*r_avg)/255*b_avg and g_avg <= b_avg*b_avg/255:
            return "BLUE"
        elif g_min >= 64 and numpy.max([b_avg, r_avg]) < g_avg*(1 - g_avg/510) and numpy.max([b_avg, r_avg]) < g_avg-48:
            return "GREEN"
        elif r_min >= 64 and b_avg < r_avg/3 and g_avg < r_avg/4 and numpy.max([b_avg, r_avg]) < g_avg-48:
            return "RED"
        elif numpy.mean([b_avg, g_avg, r_avg]) < 64 and numpy.max([b_max, g_max, r_max]) < 80:
            return "BLACK"
        elif numpy.mean([b_avg, g_avg, r_avg]) > 215 and numpy.min([b_min, g_min, r_min]) > 199:
            return "WHITE"
        
        elif numpy.max([b_std, g_std, r_std]) < 8:
            return "PURITY"
        
        elif numpy.std([b_avg, g_avg, r_avg]) < 7 and numpy.max([b_std, g_std, r_std]) < 10:
            return "GREY"
        
        return "OTHER_SOLID_COLOR"






from PyQt5.QtCore import QThread    # 导入线程模块
class Thread(QThread):   
    def __init__(self):
        super(Thread, self).__init__()

    def run(self): 
        try:
            uvc = UVCUtils()
            try:
                logger.info("......执行帧率稳定性检测......")
                uvc.openUVC()
                time.sleep(1)
            except Exception as e:
                logger.error("error:{}".format(e))
            finally:
                uvc.stopUVC()
        except Exception as e:
            logger.error("执行异常:{}".format(e))
            exit(1)
        finally:
            logger.info("......执行完成......")

