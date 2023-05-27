import time
import subprocess
import os
from PyQt5.QtCore import QThread    # 导入线程模块
class Thread(QThread):   
    def __init__(self,ip):
        super(Thread, self).__init__()
        self.ip = str(ip).replace(':5555','')
        self.stop = True
      
    def run(self):
        with open("logcat.log", 'a', encoding='utf-8') as f:
            self.logcat_file = f
            self.logcat_file.write(
                'start logcat at %s' % time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))
            self.logcat_file.write('\r\n')
            cmds = ["adb", '-s', self.ip, 'logcat', '-v', "time"]
            print(cmds)
            out = subprocess.Popen(cmds, stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding='utf-8')
            while self.stop:
                self.logcat_file.write(out.stdout.readline())
    
               
    def stop(self):
        self.stop = False

            
    
        