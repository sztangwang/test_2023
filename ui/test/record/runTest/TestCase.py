import re
import subprocess
import time
import cv2
import serial
import String
import win32com
import pythoncom
import win32api
import win32com.client
import win32con
import win32gui
from Util import TAdb
from Util import TFile
from Util import TPicture
from PyQt5.QtCore import QMutex, QWaitCondition
from networkx.tests.test_convert_numpy import np
from PIL import Image, ImageChops


class TestCase:
    def __init__(self, mainwindow, console_signal, except_image_signal):
        self.mutex = QMutex()
        self.cond = QWaitCondition()
        self.mainwindow = mainwindow
        self.console_signal = console_signal
        self.except_image_signal = except_image_signal



   

    def pc_send_string_test(self, items_value):
        """ 电脑发送字符串 """
        post = TFile.get_config_value('SendStrPostEnter')
        pre = TFile.get_config_value('SendStrPreEnter')
        pythoncom.CoInitialize()
        shell = win32com.client.Dispatch("WScript.Shell")
        if pre == 'True':
            shell.SendKeys("~")
            time.sleep(1)
        keys = items_value.split(' ')
        for i in keys:
            if str(i).find('#') != -1:  # 由于脚本采用:符号分割，所以串口发送采用#符号代替转换
                i = str(i).replace('#', ':')
            if i == 'enter':
                shell.SendKeys("~")
            if i == 'ctrl+c':
                strs = str(win32gui.GetCursorInfo()).replace('(', '').replace(')', '').split(',')
                x = int(strs[2])
                y = int(strs[3])
                self.mouse_click(x, y - 200)
                time.sleep(1)
                win32api.keybd_event(17, 0, 0, 0)  # ctrl键位码是17
                win32api.keybd_event(67, 0, 0, 0)  # v键位码是86
                win32api.keybd_event(67, 0, win32con.KEYEVENTF_KEYUP, 0)  # 释放按键
                win32api.keybd_event(17, 0, win32con.KEYEVENTF_KEYUP, 0)
                time.sleep(1)
                self.mouse_click(x, y)
            else:
                shell.SendKeys(i)
                shell.SendKeys(" ")
        time.sleep(2)
        if post == 'True':
            shell.SendKeys("~")

    def image_comparison_test(self,content):
        file = TFile.get_cache_picture(keyword = "Log")
        TFile.is_screenshot = file
        time.sleep(0.5)
        image_path = content
        self.console_signal.emit('最新图：%s'%(file), 'black')
        self.console_signal.emit('对比图：%s'%(image_path), 'black')
        self.console_signal.emit('对比值：%s'%(value), 'black')
        result = TPicture.get_opencv_image_comparison(file,image_path)
        self.console_signal.emit('结果值：%s'%(result), 'blue')
        if result > value:
            split_image = TPicture.set_picture_split(image_path,file)
            self.except_image_signal.emit(split_image)
            return False
        return True
    
    def pc_screen_comparison_test(self,content):
        x = int((re.findall(r'x(.+?),', content))[0])
        y = int((re.findall(r'y(.+?),', content))[0])
        value = int((re.findall(r'对比值:(.+?),', content))[0])
        image_path = (re.findall(r'对比图:(.+?)$', content))[0]
        file = TPicture.get_pc_screen(x,y,keyword="Log")
        time.sleep(0.5)

        result = TPicture.get_opencv_image_comparison(file,image_path)
        self.console_signal.emit('最新图：%s'%(file), 'black')
        self.console_signal.emit('对比图：%s'%(image_path), 'black')
        self.console_signal.emit('结果值：%s'%(result), 'blue')
        if result > value:
            split_image = TPicture.set_picture_split(image_path,file)
            self.runExceptImageView_signal.emit(split_image)
            return False
        return True

  

    def adb_match(self,content):
        input_value = ((re.findall(r'输入数据(.+?),', content))[0])
        print(input_value)
        

        if content.count(String.Not_Match) > 0:
            TAdb.adb_send_key(input_value)
            self.console_signal.emit(String.Not_Match, 'lime')
            return
        output_value = ((re.findall(r'预输出数据(.+?),', content))[0])
        num_value = int((re.findall(r'循环次数(.+?)$', content))[0])
        print(output_value)
        print(num_value)

     
        



    def mouse_xy_test(self,items_value):
        """ 模拟鼠标点击坐标XY """

        x = int((re.findall(r'x(.+?),',items_value))[0])
        y = int((re.findall(r'y(.+?)$',items_value))[0])
        win32api.SetCursorPos([x, y])
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)


    def audio_mean_test(self, items_value, stream):
        """ 声音均值检测 """
        audio_value = int((re.findall(r',(.+?)$', items_value))[0])
        time_value = int((re.findall(r'(.+?)秒内', items_value))[0])
        type_value = (re.findall(r'分贝值(.+?)则', items_value))[0]
        AudioList = []

        for i in range(0, time_value * 18):
            data = stream.read(1024)
            audio_data = np.fromstring(data, dtype=np.short)
            temp = np.max(audio_data)
            self.console_signal.emit('声音值:%s' % temp, 'orange')
            AudioList.append(temp)

        average = int(sum(AudioList) / len(AudioList))
        self.console_signal.emit('声音实际值:%s' % average, 'lime')
        self.console_signal.emit('声音对比值:%s' % audio_value, 'lime')
        self.console_signal.emit('声音对比值类型:%s' % type_value, 'lime')

        if items_value.count('小') != 0 and average < int(audio_value):
            self.console_signal.emit('声音值偏小', 'red')
            self.play.loop_play(self.mainwindow)
            self.play.is_loopPlay = True

        if items_value.count('大') != 0 and average > int(audio_value):
            self.console_signal.emit('声音值偏大', 'red')
            self.play.loop_play(self.mainwindow)
            self.play.is_loopPlay = True

    def serial_test(self, items_value):
        """串口检测"""
        input_value = ((re.findall(r'输入数据(.+?),', items_value))[0])
        output_value = ((re.findall(r'预输出数据(.+?),', items_value))[0])
        serial_list = ((re.findall(r'串口号(.+?),', items_value))[0]).split('|')
        serial_list = list(filter(lambda x: x != '', serial_list))
        num_value = int((re.findall(r'循环次数(.+?)$', items_value))[0])
        for num in range(0, num_value):
            for i in serial_list:
                try:
                    s = serial.Serial("COM" + i, 115200)  # 初始化串口
                except serial.serialutil.SerialException as e:
                    self.console_signal.emit('串口被占用COM:%s' % i, 'red')
                    self.play.loop_play(self.mainwindow)
                    self.play.is_loopPlay = True
                    break
                if input_value != 'Ctrl+':
                    inputStr = bytes('\n%s\n' % input_value, encoding="utf8")
                    s.write(inputStr)
                else:
                    s.write(chr(0x3).encode())  # ctrl+
                time.sleep(2)
                strs = str(s.read(s.inWaiting()), encoding="utf8")
                s.close()
                if items_value.count('不做判断') > 0:
                    self.console_signal.emit('不做判断', 'lime')

                if items_value.count('找不到') >0:
                    if strs.count(output_value) < 1:
                        self.console_signal.emit(strs, 'red')
                        self.console_signal.emit('串口COM:%s,找不到:%s,测试:Fail' % (i,output_value), 'red')
                        self.play.loop_play(self.mainwindow)
                        self.play.is_loopPlay = True
                    else:
                        self.console_signal.emit('串口COM:%s,找到:%s,测试:Pass' % (i, output_value), 'lime')

                if items_value.count('找到') > 0:
                    if strs.count(output_value) > 0:
                        self.console_signal.emit(strs, 'red')
                        self.console_signal.emit('串口COM:%s,找到:%s,测试:Fail' % (i, output_value), 'red')
                        self.play.loop_play(self.mainwindow)
                        self.play.is_loopPlay = True
                    else:
                        self.console_signal.emit('串口COM:%s,找不到:%s,测试:Pass' % (i, output_value), 'lime')
                        self.play.loop_play(self.mainwindow)
                        self.play.is_loopPlay = True


    def image_similarity_vectors_via_numpy(self, img1, img2):
        """ 图像相识度检测 """
        rgbs = 80
        im = ImageChops.difference(img2, img1)
        pix = im.load()
        width = im.size[0]
        height = im.size[1]
        val = 0
        for x in range(width):
            for y in range(height):
                r, g, b = pix[x, y]
                if r > rgbs or g > rgbs or b > rgbs:
                    val = val + 1
        return val
