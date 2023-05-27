
import os
import subprocess
import sys
import numpy as np
from dataclasses import dataclass
import time
from pathlib import Path
from queue import Queue
from threading import Thread
import cv2
from ui.test.uvc_test.log_uru import Logger

def get_project_path():
    return os.path.dirname(os.path.abspath(__file__))
sys.path.append(get_project_path())

logger = Logger().get_logger

queue = Queue()
STOP_THREAD = False

fps_queue = Queue()

@dataclass
class UVCData:
    width: int
    height: int
    show_fps: bool
    default_fps: int
    types: str
    run_time:int

def compare(last_hash, current_hash):
    return last_hash == current_hash


def kill_pid():
    # 通过pid杀死进程
    subprocess.Popen("taskkill /F /T /PID " + str(os.getpid()), shell=True)

def countdown_end(timeout=15,device=None):
    while timeout > 0:
        if device is not None:
            logger.info("当前设备：{}".format(device))
            return
        logger.info("倒计时{}秒".format(timeout))
        time.sleep(1)
        timeout-=1
    logger.debug("倒计时结束了，但是还没有开启uvc...程序退出啦!!!")
    sys.exit(0)


def time_convert(now):
    timeArray = time.localtime(now)
    otherStyleTime = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
    return otherStyleTime

def second_to_time(second):
    m, s = divmod(second, 60)
    h, m = divmod(m, 60)
    return "%02d:%02d:%02d" % (h, m, s)

@dataclass
class FrameEntity:
    last_frame: any
    current_frame: any
    last_fps: any
    current_fps: any
    diff_time:any

@dataclass
class FPSEntity:
    last_fps: any
    current_fps: any

@dataclass
class FpsFrame:
    frame: any
  


class UVCUtils:
    def __init__(self,period=1,sleep=1,exec_action=1):
        self.stop = False
        self.cv2 = cv2
        self.capture = None
        self.start_time = 0
        self.period = period
        self.last_hash = None
        self.last_frame = None
        self.last_fps = 0
        self.toc = 0.0
        self.tic = 0.0
        self.sleep = sleep
        self.exec_action = exec_action
        self.last_time_fps = 0.0
        self.frame_queue = Queue()
        self._data = {} 


    # 蓝色接口是usb3.0 usb2.0默认最高分辨率输出是720
    def openUVC(self, data: UVCData, callback=None):
        if self.stop:
            self.stop = False
        try:
            self.capture = self.cv2.VideoCapture(0)
            assert self.capture.isOpened(), "Could not open video device"
            self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, data.width)
            self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, data.height)
            self.capture.set(5, data.default_fps)
           
            if data.types is not None:
                self.capture.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*data.types))  # YUYV，MJPG，YV12

            width = self.capture.get(cv2.CAP_PROP_FRAME_WIDTH)
            height = self.capture.get(cv2.CAP_PROP_FRAME_HEIGHT)
            logger.debug("CAP_PROP_FOURCC:{}".format(self.capture.get(cv2.CAP_PROP_FOURCC)))
            logger.debug(f"Screen resolution :{width} * {height}")
            pos_frame = self.capture.get(cv2.CAP_PROP_POS_FRAMES)
            path = "%s/images/"%Path(__file__).resolve().parents[0]
            for i in os.listdir(path):
                c_path = os.path.join(path, i)
                os.remove(c_path)       # 删除所有图片
            start_time = time.time()
           
            while self.capture.isOpened():
                ret, frame = self.capture.read()
                if ret:
                    if time.time() - start_time > data.run_time: # 判断是否大于设置的运行设置，大于则结束测试
                        self.capture.release()
                        break
                    if STOP_THREAD:
                        self.stopUVC()
                    if data.show_fps:
                        self.frame_queue.put(frame)
                else:
                    self.capture.set(cv2.CAP_PROP_POS_FRAMES, pos_frame - 1)
                    cv2.waitKey(1000)
                    self.capture.open(0)
                    continue
            print('保存图片中...',self.frame_queue.qsize())
            for i in range(self.frame_queue.qsize()): 
                if i == 0:
                    Last_frame = self.frame_queue.get()
                    self.cv2.imwrite("%s/%s.png"%(path,i),Last_frame)
                if i != 0:
                    current_frame = self.frame_queue.get()
                    if self.opencv_diff(Last_frame,current_frame):
                        print("图片：%s.png,与上一张图片对比相似"%(i))
                    self.cv2.imwrite("%s/%s.png"%(path,i),current_frame)
                    Last_frame = current_frame
        except Exception as e:
            logger.error("openUVC error:{}".format(e))
            self.stopUVC()
            kill_pid()


    def opencv_diff(self,img1,img2):
        gray_base = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
        gray_cur = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)
        resImg = cv2.absdiff(gray_cur, gray_base)
        # threshold阈值函数(原图像应该是灰度图,对像素值进行分类的阈值,当像素值高于（有时是小于）阈值时应该被赋予的新的像素值,阈值方法)
        thresh = cv2.threshold(resImg, 30, 255, cv2.THRESH_BINARY)[1]
        # 用一下腐蚀与膨胀
        thresh = cv2.dilate(thresh, None, iterations=2)
        # findContours检测物体轮廓(寻找轮廓的图像,轮廓的检索模式,轮廓的近似办法)
        contours, hierarchy = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        for c in contours:
            # 设置敏感度
            # contourArea计算轮廓面积
            if cv2.contourArea(c) > 600:
                return False
        return True

    def stopUVC(self):
        self.toc = time.perf_counter()  # 结束计时
        # 持续时间
        run_times = round(self.toc - self.tic, 2)
        times = second_to_time(run_times)
        with open("result_{}.txt".format("YVY2"),'a') as f:
            f.write("运行的总时间：{}".format(times))
        logger.info(f"持续时间: {times} ")
        self.stop = True
        # 恢复self.sleep的值
        self.sleep = 1
        self.capture.release()
        self.cv2.destroyAllWindows()






from PyQt5.QtCore import QThread    # 导入线程模块
class Thread(QThread):   
    def __init__(self,type,width,height,fps,count,period,sleep,run_time):
        super(Thread, self).__init__()
        self.type = type
        self.width = width
        self.height = height
        self.fps = fps
        self.count = count
        self.period = period
        self.sleep = sleep
        self.run_time = run_time

    def run(self): 
        try:
            logger.debug("type:{},width:{},height:{},fps:{},count:{},period:{},sleep:{}".format(self.type, self.width, self.height, self.fps, self.count, self.period, self.sleep))
           
            uvc = UVCUtils(period=self.period)
            try:
                logger.info("......执行帧率稳定性检测......")
            
                uvc.openUVC(UVCData(width=self.width, height=self.height, show_fps=True, default_fps=self.fps,types=self.type,run_time=self.run_time))
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

