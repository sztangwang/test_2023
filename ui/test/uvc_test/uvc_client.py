# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import os
import argparse
import subprocess
import sys
from dataclasses import dataclass
import time
from queue import Queue
from threading import Thread
import cv2
import imagehash
import numpy
from PIL import Image
from imutils.video import FPS
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
    fps: any
    current_fps_time: any


class ConsumerImgThread(Thread):
    def __init__(self,exec_action=1):
        super().__init__()
        self._stop = False
        self.true_count = 0
        # 前一帧的fps
        self.last_fps = 0
        # 当前帧的fps
        self.current_fps = 0
        # 卡顿的次数
        self.stuck_count = 0
        # 掉帧的次数
        self.drop_frame_count = 0
        # 掉帧的开始时间
        self.drop_frame_start_time = 0
        # 掉帧的结束时间
        self.drop_frame_end_time = 0
        # 运行方式
        self.exec_action = exec_action
        #数据文件
        self.file_path = str(time_convert(time.time())).replace(' ','').replace(":","_")

    def stop(self):
        self._stop = True

    def run(self):
        global queue
        while not self._stop:
            frame = queue.get()
            queue.task_done()
            start_time = time.time()
            try:
                if int(self.exec_action) == 3:
                    if frame.last_frame is not None and frame.current_frame is not None:
                        self.current_fps = round(frame.current_fps, 2)
                        last_img = Image.fromarray(numpy.uint8(frame.last_frame))
                        current_img = Image.fromarray(numpy.uint8(frame.current_frame))
                        last_hash = imagehash.dhash(last_img)
                        current_hash = imagehash.dhash(current_img)
                        result = compare(last_hash, current_hash)
                        loss_time = time.time() - start_time
                        logger.debug(f"loss_time:{loss_time}")
                        logger.debug(f"Compare : {result} , Loss :{loss_time}s")
                        # 当连续n次返回都是true,说明是真的定屏了
                        if result:
                            self.true_count += 1
                        else:
                            self.true_count = 0
                        if self.true_count >= 30:
                            global STOP_THREAD
                            STOP_THREAD = True
                            self.true_count = 0
                            logger.info("定屏了,uvc测试结束！")
                            logger.info("定屏时间:{}".format(time_convert(time.time())))
                            # 结束线程
                            self.stop()
                           # 结束进程
                        # 写日志文件
                        with open("log_3.txt", "a") as f:
                            f.write("当前时间：{},当前帧率：{} \n".format(time_convert(time.time()), self.current_fps))
                else:
                    if frame.last_fps is not None and frame.current_fps is not None:
                        self.last_fps = round(frame.last_fps,2)
                        self.current_fps = round(frame.current_fps,2)
                        # 获取当前帧的时间戳
                        # current_fps_time =frame.current_fps_time
                        # # 获取前一帧的时间戳
                        # last_fps_time =frame.last_fps_time
                        # # 计算帧的时间戳差值
                        # time_diff =current_fps_time -last_fps_time
                        logger.debug("time_diff------------>{}".format(frame.diff_time))
                        logger.debug(f"FPS:{self.current_fps} , Last FPS:{self.last_fps}")
                        #  print(f"FPS:{self.current_fps} , Last FPS:{self.last_fps}")
                        fps_diffs = self.last_fps - self.current_fps
                        logger.debug(f"FPS:{self.current_fps} , Last:{fps_diffs}")
                        # print(f"FPS:{self.current_fps} , Last:{fps_diffs}")
                        if 3 > fps_diffs > 1:
                            self.drop_frame_count += 1
                            logger.info(f"掉帧次数：{self.drop_frame_count}")
                            if self.drop_frame_count == 1:
                                self.drop_frame_start_time = time.time()
                                logger.info(f"掉帧开始时间：{time_convert(self.drop_frame_start_time)}")
                                with open("drop_frame_start_time.txt", "a") as f:
                                    f.write("掉帧开始时间：{}, 掉帧次数：{} \n".format(str(time_convert(self.drop_frame_start_time)), str(self.drop_frame_count)))
                            elif self.drop_frame_count > 1:
                                self.drop_frame_end_time = time.time()
                                logger.info(f"掉帧结束时间：{time_convert(self.drop_frame_end_time)}")
                                drop_frame_time = self.drop_frame_end_time - self.drop_frame_start_time
                                with open("drop_frame_end_time.txt", "a") as f:
                                    f.write("掉帧结束时间：{}, 掉帧次数：{} \n".format(str(time_convert(self.drop_frame_end_time)), str(self.drop_frame_count)))
                                if drop_frame_time > 3:
                                    logger.info(f"掉帧超过3秒")
                                    with open("drop_frame_3.txt", "a") as f:
                                        f.write("掉帧开始时间：{} , 掉帧持续时间：{} ,掉帧次数：{}, 当前帧率：{},前一帧帧率：{} \n".format(
                                            time_convert(self.drop_frame_start_time),
                                            drop_frame_time,
                                            self.drop_frame_count,
                                            self.current_fps,
                                            self.last_fps))
                                    self.drop_frame_count = 0
                                    self.drop_frame_start_time = 0
                                    self.drop_frame_end_time = 0
                        # 帧率差值大于3表示卡顿，记录卡顿次数，卡顿时间
                        elif fps_diffs > 3:
                            self.stuck_count += 1
                            logger.info(f"卡顿次数：{self.stuck_count}")
                            if self.stuck_count == 1:
                                self.drop_frame_start_time = time.time()
                                logger.info(f"卡顿开始时间：{time_convert(self.drop_frame_start_time)}")
                                with open("stuck_frame_start_time.txt", "a") as f:
                                    f.write("卡顿开始时间：{}, 卡顿次数：{} \n".format(str(time_convert(self.drop_frame_start_time)), str(self.stuck_count)))
                            elif self.stuck_count > 1:
                                self.drop_frame_end_time = time.time()
                                logger.info(f"卡顿结束时间：{time_convert(self.drop_frame_end_time)}")
                                drop_frame_time = self.drop_frame_end_time - self.drop_frame_start_time
                                with open("stuck_frame_end_time.txt", "a") as f:
                                    f.write("卡顿结束时间：{}, 卡顿次数：{} \n".format(str(time_convert(self.drop_frame_end_time)), str(self.stuck_count)))
                                if drop_frame_time > 3:
                                    logger.info(f"卡顿超过3秒")
                                    # 将日志写入到文件中
                                    with open("stuck_3.txt", "a") as f:
                                        f.write("卡顿开始时间：{} , 卡顿持续时间：{} ,卡顿次数：{}, 当前帧率：{},前一帧帧率：{} \n".format(
                                            time_convert(self.drop_frame_start_time),
                                            drop_frame_time,
                                            self.stuck_count,
                                            self.current_fps,
                                            self.last_fps))
                                    self.stuck_count = 0
                                    self.drop_frame_start_time = 0
                                    self.drop_frame_end_time = 0
                        else:
                            # 输入写入到csv文件中
                            # with open("result_{}.csv".format("YVY2"), "a") as f:
                           with open("result_{}.csv".format(self.file_path), "a") as f:
                                f.write("{},{},{},{} \n".format(time_convert(time.time()), self.current_fps, self.last_fps,frame.diff_time))
                            # with open("result_{}.txt".format(type), "a") as f:
                            #     f.write("当前时间：{} \t,当前帧率：{} \t,前一帧帧率：{} \t,两帧之间的时间差：{} \t \n".format(time_convert(time.time()), self.current_fps, self.last_fps,time_diff))
                                self.drop_frame_count = 0
                                self.stuck_count = 0
                                self.drop_frame_start_time = 0
                                self.drop_frame_end_time = 0
            except Exception as e:
                self.stop()





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


    def callback(self,fpsFrame):
        if self.last_fps is not None:
            if self.last_time_fps ==0.0:
                self.last_time_fps = fpsFrame.current_fps_time
            else:
                self.diff_time = fpsFrame.current_fps_time - self.last_time_fps
                self.last_time_fps = fpsFrame.current_fps_time
            if self.last_frame is not None and self.last_fps is not None:
                f = FrameEntity(self.last_frame, fpsFrame.frame,self.last_fps,fpsFrame.fps,self.diff_time)
                global queue
                queue.put(f)
            self.last_frame = fpsFrame.frame
            self.last_fps = fpsFrame.fps
            self.start_time = time.time_ns()
            self.curernt_time =time.time_ns()








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
            # self.capture.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*"YVY2"))
            width = self.capture.get(cv2.CAP_PROP_FRAME_WIDTH)
            height = self.capture.get(cv2.CAP_PROP_FRAME_HEIGHT)
            logger.debug("CAP_PROP_FOURCC:{}".format(self.capture.get(cv2.CAP_PROP_FOURCC)))
            logger.debug(f"Screen resolution :{width} * {height}")
            # 取队列中取数据
            self.tic = time.perf_counter()  # 开始计时
            pos_frame = self.capture.get(cv2.CAP_PROP_POS_FRAMES)
            start_time = time.time()

            fps = FPS().start()
            while self.capture.isOpened():
                ret, frame = self.capture.read()
                if ret:
                    fps.update()
                    fps.stop()
                    current_fps = fps.fps()
                    # 保存当前帧的时间戳
                    current_fps_time = time.time_ns()

                    if time.time() - start_time > data.run_time: # 判断是否大于设置的运行设置，大于则结束测试
                        break
                    if callback is not None:
                        fps_frame=FpsFrame(frame,current_fps,current_fps_time)
                        # callback(frame)
                        callback(fps_frame)
                    if STOP_THREAD:
                       # print("STOP_THREAD。。。")
                        self.stopUVC()
                    self.toc = time.perf_counter()   # 结束计时
                    if int(self.exec_action) == 2:
                        if int(self.toc - self.tic) >= self.sleep:
                            # 重置计时器
                            self.tic = time.perf_counter()
                            logger.debug("运行时间到，结束执行.")
                            break
                    if data.show_fps:
                        run_times = round(self.toc - self.tic, 2)
                        times = second_to_time(run_times)
                        strs= "FPS:{:.2f}".format(current_fps) + "run_time: {}".format(times)+"Resolution:{}*{}".format(width, height)
                        self.cv2.putText(frame,
                                         strs, (50, 50),
                                             cv2.FONT_HERSHEY_DUPLEX, 2, (0, 255, 255),
                                             1)
                        self.cv2.imshow('webCam', frame)
                        if self.cv2.waitKey(1) == ord('s'):
                            break
                        if self.cv2.getWindowProperty('webCam', 0) == -1:
                            break
                else:
                    self.capture.set(cv2.CAP_PROP_POS_FRAMES, pos_frame - 1)
                    print("frame is not ready")
                    cv2.waitKey(1000)
                    self.capture.open(0)
                    continue
                if self.capture.get(cv2.CAP_PROP_POS_FRAMES) == self.capture.get(cv2.CAP_PROP_FRAME_COUNT):
                    # If the number of captured frames is equal to the total number of frames,
                    # we stop
                    logger.debug("captured frames is equal to the total number of frames")
                    break
        except Exception as e:
            logger.error("openUVC error:{}".format(e))
            self.stopUVC()
            kill_pid()


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



def main():
    # 启动uvc 定屏检测
    logger.info("启动uvc检测...")
    logger.info("start_time:{}".format(time.time()))
    uvc = UVCUtils(period=1)
    c = ConsumerImgThread()
    c.start()
    uvc.openUVC(UVCData(width=1920, height=1080, show_fps=True, default_fps=30,type="YVY2"), callback=uvc.callback)
    time.sleep(1)
    # 3840,2160



from PyQt5.QtCore import QThread    # 导入线程模块
class Thread(QThread):   
    def __init__(self,type,width,height,fps,count,period,sleep,exec_action,run_time):
        super(Thread, self).__init__()
        self.type = type
        self.width = width
        self.height = height
        self.fps = fps
        self.count = count
        self.period = period
        self.sleep = sleep
        self.exec_action = exec_action
        self.run_time = run_time

    def run(self): 
        try:
            logger.debug("type:{},width:{},height:{},fps:{},count:{},period:{},sleep:{},exec_action:{}".format(self.type, self.width, self.height, self.fps, self.count, self.period, self.sleep,self.exec_action))
            if self.exec_action == "1":
                uvc = UVCUtils(period=self.period, exec_action=self.exec_action)
                try:
                    logger.info("......执行帧率稳定性检测......")
                    c = ConsumerImgThread()
                    c.start()
                    uvc.openUVC(UVCData(width=self.width, height=self.height, show_fps=True, default_fps=self.fps,types=self.type,run_time=self.run_time), callback=uvc.callback)
                    time.sleep(1)
                except Exception as e:
                    logger.error("error:{}".format(e))
                finally:
                    uvc.stopUVC()
            elif self.exec_action == "2":
                logger.info("......执行打开和关闭UVC操作.总共执行次数:{}......".format(self.count))
                uvc = UVCUtils(sleep=self.sleep,exec_action=self.exec_action)
                for i in range(int(self.count)):
                    # 将日志保存到文件中
                    with open('uvc_reboot.log','a') as f:
                        f.write("总共执行次数:{}\n".format(self.count))
                        f.write("第{}次执行打开关闭UVC操作 \n".format(i+1))
                        f.write("配置信息：视频类型:{},宽:{},高:{},设置帧率:{},运行次数:{},间隔周期:{},间隔时间:{},执行方式:{} \n".format(self.type, self.width, self.height, self.fps, self.count, self.period, self.sleep,self.exec_action))
                        f.write("运行时间:{} \n".format(time.time()))
                        f.write("第{}次打开UVC... \n".format(i+1))
                    logger.info("第{}次打开UVC...".format(i+1))
                    uvc.openUVC(UVCData(width=self.width, height=self.height, show_fps=True, default_fps=self.fps,types=self.type,run_time=self.run_time), callback=None)
                    with open('uvc_reboot.log', 'a') as f:
                        f.write("运行{}秒后关闭UVC \n".format(self.sleep))
                        f.write("第{}次关闭UVC \n".format(i+1))
                    logger.info("运行{}秒后关闭UVC".format(self.sleep))
                    logger.info("第{}次关闭UVC......".format(i+1))
                    uvc.stopUVC()
                    time.sleep(int(3))  # 休眠3秒
                logger.info("执行打开关闭操作完成...")
            elif self.exec_action == "3":
                uvc = UVCUtils(period=self.period)
                try:
                    logger.info("......执行定屏检测......")
                    c = ConsumerImgThread(self.exec_action)
                    c.start()
                    uvc.openUVC(UVCData(width=self.width, height=self.height, show_fps=True, default_fps=self.fps,types=self.type,run_time=self.run_time), callback=uvc.callback)
                    time.sleep(1)
                except Exception as e:
                    logger.error("error:{}".format(e))
                finally:
                    uvc.stopUVC()
            else:
                logger.info("执行动作参数错误...")
                exit(1)
        except Exception as e:
            logger.error("执行异常:{}".format(e))
            exit(1)
        finally:
            logger.info("......执行完成......")
            #kill_pid()

