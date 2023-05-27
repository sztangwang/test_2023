import time
from ctypes import *
import serial
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from Util.PlayAudio import playAudio
from Util import TFile


class RunSettings:
    def __init__(self,mainwindow,console_signal):
        self.mainwindow = mainwindow
        self.console_signal = console_signal
     
        audio_select_value = TFile.get_config_value('audio_select')
        self.play = playAudio('./res/%s'%audio_select_value)

    def settings(self):
        start = time.time()
        self.run_port_check()
        self.max_volume_setting()
        end = time.time()
        times = int(end - start)
        if times < 6:
            times = 6 - times
        else:
            return 0
        return times

    def max_volume_setting(self):
        try:
            devices = AudioUtilities.GetSpeakers()
            interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            volume = cast(interface, POINTER(IAudioEndpointVolume))
            volume.SetMute(0, None)
            volume.SetMasterVolumeLevel(0.0, None)
        except:
            print('运行调节设置声音异常')


    def run_port_check(self):
        serialList = get_port()
        for com in serialList:
            try:
                self.console_signal.emit(f"{'检测串口是否有未连接情况COM:' + com}\n", 'orange')
                s = serial.Serial("COM" + com, 115200)  # 初始化串口
                s.write(bytes('\nifconfig\n', encoding="utf8"))
                time.sleep(0.3)
                data = str(s.read(s.inWaiting()).decode('utf-8', 'ignore'))
                s.close()
                if len(data) > 3:
                    self.console_signal.emit(f"{'检测到有端口未连接COM:%s,等待5秒钟后继续运行' % com}\n", 'red')
                    self.play.once_play()
                    break
            except serial.serialutil.SerialException:
                self.console_signal.emit(f"{'串口被占用:' + com}\n", 'red')






