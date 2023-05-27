
import random
import time
import re
import pyautogui
import win32com
import pythoncom
import win32api
import win32com.client
import win32con
import win32gui
from PyQt5 import QtCore
from PyQt5.QtCore import QThread
from ui.test.record import String
from ui.test.record import Configs
from ui.test.record.Util import TUiautomator2
from ui.test.record.Util import TPicture
from ui.test.record.Util import TAdb
from ui.test.record.Util import TFile
from ui.test.record.Util import Remote
from ui.test.record.Util import TSerial



class runThread(QThread):
    console_signal = QtCore.pyqtSignal(str)
    except_image_signal = QtCore.pyqtSignal(list)
    except_msg_signal = QtCore.pyqtSignal(str)
    progress_stype_signal = QtCore.pyqtSignal()
    num_signal = QtCore.pyqtSignal()
    scrollToItem_signal = QtCore.pyqtSignal(int)

    def __init__(self, parent):
        super().__init__(parent=parent)
        self.mainwindow = parent
        self.run_thread_is_on = True
        self.serial = None
       

    def run(self):
        self.loop_num = int(TFile.get_config_value('loop_num'))
        self.table = self.mainwindow.TableWidgetView    # 步骤表格
        for row in range(0, self.table.rowCount()):
            if self.table.item(row, 0) is None:         # 获取整个表格有效的行数
                if row == 0:                            # 如果第一行没有数据表示为空表格，所以停止测试
                    self.console_signal.emit('脚本为空')
                    return
                else:
                    break
        if Configs.selection_line_run_rows:
            self.selection_line_run(Configs.selection_line_run_rows - 1)
            Configs.selection_line_run_rows = None
            return

        self.count_down(4)                               # 开始测试倒计时
        for _ in range(TFile.get_run_num() + 1, self.loop_num):
            for rows in range(0, row + 2):                # 加2表示运行过程中允许插入两行
                if not self.run_thread_is_on:
                    return
                self.scrollToItem_signal.emit(rows)
                if not self.set_item_value(rows):
                    break
                for _ in range(int(self.items_num)):
                    if not self.run_thread_is_on:
                        return
                    self.select_run_type()
                    self.progress_stype_signal.emit()
            self.num_signal.emit()
        self.console_signal.emit('循环次数为:%s' % self.loop_num)

    def selection_line_run(self,rows):
        self.console_signal.emit(rows)
        self.set_item_value(rows)
        self.select_run_type()
        self.run_thread_is_on = False

    def set_item_value(self,rows):
        try:
            self.table.item(rows, 0).text()
        except:
            return False
        self.name = self.table.item(rows, 0).text()
        self.content = self.table.item(rows, 2).text()    
        self.value = self.table.item(rows, 3).text() 
        self.types = self.table.cellWidget(rows,1).currentText()
        self.exceptions = self.table.cellWidget(rows,6).currentText()
        self.items_sleep = int(self.table.item(rows, 4).text())
        self.items_num = self.table.item(rows, 5).text()
        if self.items_num.count('~') > 0:
            items_num_list = self.items_num.split('~')
            self.items_num = random.randint(int(items_num_list[0]), int(items_num_list[1]))
        
        self.console_signal.emit('开始测试:%s' % self.name)
        self.console_signal.emit('事件内容:%s' % self.content)
        #self.console_signal.emit('预期:%s' % self.types)
        self.console_signal.emit('对比值:%s' % self.value)
        #self.console_signal.emit('休眠时间:%s' % self.items_sleep)
        self.console_signal.emit('测试次数:%s' % self.items_num)
        #self.console_signal.emit('异常类型:%s' % self.exceptions)
        return True

    def stop_thread(self):
        self.console_signal.emit('===========测试结果:Fail')
        if self.exceptions in "stop":
            self.run_thread_is_on = False
        
        
    def select_run_type(self):
        if self.name in String.Ac_On:
            if not Remote.ac_on():
                self.stop_thread()
            else:
                self.console_signal.emit('===========测试结果:Pass')

        elif self.name in String.Ac_Off:
            if not Remote.ac_off():
                self.stop_thread()
            else:
                self.console_signal.emit('===========测试结果:Pass')

        elif self.name in String.Usb_On:
            if not Remote.usb_on():
                self.stop_thread()
            else:
                self.console_signal.emit('===========测试结果:Pass')
            
        elif self.name in String.Usb_Off:
            if not Remote.usb_off():
                self.stop_thread()
            else:
                self.console_signal.emit('===========测试结果:Pass')

        elif self.name in String.Usb_Off:
            if not Remote.usb_off():
                self.stop_thread()
            else:
                self.console_signal.emit('===========测试结果:Pass')
        

        elif self.name in String.Power:
            if not Remote.power():
                self.stop_thread() 
            else:
                self.console_signal.emit('===========测试结果:Pass')
        
        elif self.name in String.Adb_Match:
            if self.types in "找不到" and self.adb_match():
                self.except_msg_signal.emit("找到：%s"%self.value)
                self.stop_thread()

            elif self.types in "找到" and not self.adb_match():
                self.except_msg_signal.emit("找不到：%s"%self.value)
                self.stop_thread()
            else:
                self.console_signal.emit('===========测试结果:Pass')
            
        elif self.name in String.Adb_Click_Coord:
            xy = self.content.split(',')
            if not TAdb.click(xy[0], xy[1]):
                self.except_msg_signal.emit('设备异常')
            else:
                self.console_signal.emit('===========测试结果:Pass')

        elif self.name in String.Serial_Click_Coord:
            xy = self.content.split(',')
            try:
                if not self.serial:
                    self.serial = TSerial.SerialPort("COM%s"%xy[2])
            except Exception as e:
                    self.console_signal.emit('串口连接被拒绝%s'%e)
                
            if not  self.serial.write("input tap %s %s"%( xy[0], xy[1])):
                self.except_msg_signal.emit('设备异常')
            else:
                self.console_signal.emit('===========测试结果:Pass')



        elif self.name in String.Adb_Send_Key:
            if not TAdb.send_key(self.content):
                self.stop_thread()
            else:
                self.console_signal.emit('===========测试结果:Pass')
            
               
        elif self.name in String.OneKey_Power:
            if not Remote.ac_off():
                self.console_signal.emit(String.Serial_Exception)
            time.sleep(4)
            if not Remote.ac_on():
                self.console_signal.emit(String.Serial_Exception)
            time.sleep(2)
            if not Remote.power():
                self.console_signal.emit(String.Serial_Exception)

        elif self.name in String.SCREEN_EXCEPTION_TEST:
            file = TFile.get_cache_picture(keyword = "Log")
            self.console_signal.emit('%s：%s'%(String.SCREENSHOT,file))
            TFile.is_screenshot = file
            time.sleep(0.5)
            picture_status = TPicture.get_picture_status(file,is_cut=True)
            self.console_signal.emit('结果：%s'%(picture_status))

            if picture_status not in String.OTHER_SOLID_COLOR:
                self.stop_thread()
                self.except_image_signal.emit(file)

        elif self.name in String.Image_Comparison:
            if not self.image_comparison_test():
                self.stop_thread()


        elif self.name in String.PC_Screen_Comparison:
            if not self.pc_screen_comparison_test():
                self.stop_thread()

        elif self.name in String.PC_Mose:
            x = int((re.findall(r'x(.+?),', self.content))[0])
            y = int((re.findall(r'y(.+?)$', self.content))[0])
            self.pc_mouse_click(x,y)
            

        elif self.name in String.PC_Send_String:
            if not self.pc_send_string_test():
                self.stop_thread()

        elif self.name in String.Adb_activity:
            activity = TAdb.app_current_match(activity=self.value,match=True)
            if not activity and self.types in "找到":
                self.stop_thread()
                self.except_msg_signal.emit('结果值:%s'%(activity))
            elif activity and self.types in "找不到":
                self.stop_thread()
                self.except_msg_signal.emit('结果值:%s'%(activity))
            self.console_signal.emit('结果值:%s'%(activity))
            

        elif self.name in String.Adb_package:
            package = TAdb.app_current_match(package=self.value,match=True)
            if not package and self.types in "找到":
                self.stop_thread()
                self.except_msg_signal.emit('结果值:%s'%(package))
            elif package and self.types in "找不到":
                self.stop_thread()
                self.except_msg_signal.emit('结果值:%s'%(package))
            self.console_signal.emit('结果值:%s'%(package))
            
        elif self.name in String.Adb_App_start:
            package = ((re.findall(r'package=\'(.+?)\',', self.value))[0])
            activity = ((re.findall(r'activity=\'(.+?)\',', self.value))[0])
            TAdb.app_start(package_name=package,activity=activity)

        elif self.name in String.serial_test:
            self.serial_test()
            
        elif self.name in "9805串口匹配":
            self.serial_test_9805()
        
        elif self.name in ['ui2_Xpath点击','ui2_resourceId点击','ui2_文本点击',"ui2_Text与resourceId点击"]:
            if not TUiautomator2.click(self.content,TFile.get_config_value("CurrentDevice")):
                self.stop_thread()

        elif self.name in ['ui2_文本断言','ui2_resourceId断言']:
            self.result_out(TUiautomator2.exist(self.content,TFile.get_config_value("CurrentDevice")))
           
        self.count_down(self.items_sleep)

    def result_out(self,result):
        if not result and self.types in "找到":
            self.stop_thread()

        elif result and self.types in "找到":
            self.console_signal.emit('===========测试结果:Pass')

        elif not result and self.types in "找不到":
            self.console_signal.emit('===========测试结果:Pass')
        
        elif result and self.types in "找不到":
            self.stop_thread()


    def serial_test(self):
        port = ((re.findall(r'串口(.+?)$', self.content))[0])
        try:
            input = ((re.findall(r'输入数据(.+?),串口', self.content))[0])
        except:
            input = None
        try:
            if not self.serial:
                self.serial = TSerial.SerialPort("COM%s"%port)
        except Exception as e:
            self.console_signal.emit('串口连接被拒绝%s'%e)

        if input: #是否写入数据
            self.serial.write(input)

        if self.value:  # 是否匹配
            res = self.serial.read_grep(self.value)
            if res and  self.types in "找不到": 
                self.console_signal.emit('匹配结果：%s'%res)
                self.stop_thread()

            elif not res and self.types in "找到":
                self.console_signal.emit('匹配结果：%s'%res)
                self.stop_thread()

        if self.run_thread_is_on:
            self.console_signal.emit('===========测试结果:Pass')

      

    def serial_test_9805(self):
        port = ((re.findall(r'串口(.+?)$', self.content))[0])
        input = ((re.findall(r'(.+?),匹配数据', self.content))[0])
        match = eval((re.findall(r'匹配数据(.+?),串口', self.content))[0])
        try:
            if not self.serial:
                self.serial = TSerial.SerialPort("COM%s"%port)
            self.console_signal.emit(self.serial)
        except Exception as e:
            self.console_signal.emit('串口连接被拒绝%s'%e)
        self.serial.write(input)      # 串口写入
        data = self.serial.read_all() # 串口读取
        data_list = data.split('\n') # 数据分割
        is_find = True           # 控制找下一行标志
        for key in match:
            is_key = False
            for i ,line in enumerate(data_list): #数据遍历
                line_list = list(filter(lambda x: x.strip(), line.split(' '))) # 数据根据行分割为数组
                if not is_find:
                    is_key = True # 控制
                    self.console_signal.emit('==============%s'%(text))
                    try:
                        reality = line_list[index]
                        excepts = match[key][1]
                        differ = match[key][2]
                    except:
                        self.stop_thread()
                        break

                    self.console_signal.emit('实际值：%s'%(reality))
                    self.console_signal.emit('预期值：%s'%(excepts))
                    self.console_signal.emit('偏差设置值：%s'%(differ))
                    if differ == '': # 偏差值等于空
                        if reality == excepts:  # 实际值等于预期值
                            self.console_signal.emit('===========测试结果:Pass')
                        else:
                            self.stop_thread()
                    else:
                        reality = int("".join(list(filter(str.isdigit, reality)))) # 保留数字
                        if int(abs(reality - int(excepts))) <= int(differ):
                            self.console_signal.emit('===========测试结果:Pass')
                        else:
                            self.stop_thread()
                    is_find = True

                if match[key][0] in line_list and is_find:  #只匹配第0为，第一位为预期结果，第二位为偏差值
                    #self.console_signal.emit('行数据：%s'%line_list)
                    index = line_list.index(match[key][0])
                    #self.console_signal.emit("第几位：%s"%index)
                    text = match[key][0]
                    #self.console_signal.emit("找到：",text)
                    is_find = False
            if not is_key and match[key][0]:
                #self.console_signal.emit('未匹配到：%s'%match[key][0])
                self.stop_thread()

    


    def count_down(self,items_sleep):
        """ 倒计时函数 """
        if str(items_sleep).count('~') != 0:
            items_sleep_list = items_sleep.split('~')
            items_sleep = random.randint(int(float(items_sleep_list[0])), int(float(items_sleep_list[1])))
        time_start = time.time()
        t = 0
        while self.run_thread_is_on:
            if time.time() - time_start > items_sleep:
                break
            else:
                self.progress_stype_signal.emit()
                self.console_signal.emit('%s秒休眠倒计时:%s'%(items_sleep,t))
            time.sleep(1)
            t = t + 1

    def pc_mouse_click(self,x,y):
        try:
            pyautogui.click(x, y, button='left')
        except:
            time.sleep(1)
            pyautogui.click(x, y, button='left')


    def pc_send_string_test(self):
        pythoncom.CoInitialize()
        shell = win32com.client.Dispatch("WScript.Shell")
        
        shell.SendKeys("~")
        time.sleep(1)

        if self.content in 'enter':
            shell.SendKeys("~")
            return
        elif self.content in 'ctrl+c':
            strs = str(win32gui.GetCursorInfo()).replace('(', '').replace(')', '').split(',')
            x = int(strs[2])
            y = int(strs[3])
            self.pc_mouse_click(x, y - 200)
            time.sleep(1)
            win32api.keybd_event(17, 0, 0, 0)  # ctrl键位码是17
            win32api.keybd_event(67, 0, 0, 0)  # v键位码是86
            win32api.keybd_event(67, 0, win32con.KEYEVENTF_KEYUP, 0)  # 释放按键
            win32api.keybd_event(17, 0, win32con.KEYEVENTF_KEYUP, 0)
            time.sleep(1)
            self.pc_mouse_click(x, y)
        else:
            pyautogui.typewrite(self.content,interval=0.25)


        time.sleep(1)
        shell.SendKeys("~")
        return True

    def pc_screen_comparison_test(self):
        """ 电脑截图对比测试 """
        x = int((re.findall(r'x(.+?),', self.content))[0])
        y = int((re.findall(r'y(.+?),', self.content))[0])
        image_path = (re.findall(r'对比图:(.+?)$', self.content))[0]
        file = TPicture.get_pc_screen(x,y,keyword="Log")
        time.sleep(0.5)

        result = TPicture.get_opencv_image_comparison(file,image_path)
        if result > int(self.value):
            self.console_signal.emit('结果值：%s'%(result))
            self.except_image_signal.emit([image_path,file])
            time.sleep(1)
            return False
        self.console_signal.emit('结果值：%s'%(result))
        return True


    def image_comparison_test(self):
        """ 图像对比测试"""
        Configs.screenshot_file = None
        Configs.is_screenshot = TFile.get_cache_picture(keyword = "Log")
        
        start_time = time.time()
        while time.time() - start_time < 5:
            if Configs.screenshot_file:
                time.sleep(0.2)
                break
        try:
            result = TPicture.get_opencv_image_comparison(Configs.screenshot_file,self.content)
        except Exception as e:
            self.console_signal.emit(e)
            self.except_msg_signal.emit('图像异常')
            return False
        if result > int(self.value) and self.exceptions == "stop":
            self.console_signal.emit('结果值：%s'%(result))
            self.except_image_signal.emit([self.content,Configs.screenshot_file])
            time.sleep(1)
            return False
        self.console_signal.emit('结果值：%s'%(result))
        return True
    
    def adb_match(self):
        input_value = ((re.findall(r'(.+?),', self.content))[0])
        CurrentDevice = TFile.get_config_value("CurrentDevice")
        input_value = input_value.replace('adb','adb -s %s'%CurrentDevice)
        res = TAdb.adb_send_key(input_value,match=self.value)
        self.console_signal.emit("结果：%s"%res )  
        return res