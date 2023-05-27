import os
import re
import shutil
import time
import zipfile
from decimal import Decimal
import requests
from PyQt5.QtCore import QThread


class Update(QThread):
    def __init__(self, console_signal):
        super().__init__()
        self.console_signal = console_signal
        self.version_path = 'C:/TestTime/2/'
        self.version_path2 = 'C:/TestTime/2/update/'
        self.zip_file = 'C:/TestTime/2/sztangwang-main.zip'
        self.zip_file2 = 'C:/TestTime/2/sztangwang-main/update2.zip'
        self.zip_url = 'https://codeload.github.com/sztangwang/sztangwang/zip/refs/heads/main'

    def run(self):
        self.check_updates()


    def check_updates(self):
        self.console_signal.emit('正在检测更新，请稍等...', 'lime')
        try:
            os.remove(self.version_path2)
        except:
            pass
        try:
            os.makedirs(self.version_path2)
        except:
            pass
        try:
            version_text = str(requests.get('https://abf.qjdedsc.com/?a=getT').text)
        except:
            self.console_signal.emit('网络异常,电脑网络不稳定', 'red')
            return

        self.new_version = (re.findall(r"version2:(.*?)\n", version_text))[0]

        with open(self.version_path + 'version.txt', 'r', encoding='utf-8') as f1:
            version = f1.read()  # 读取当前版本

        if float(self.new_version) > float(version):  # 版本对比
            with open('./autoupdata', 'w+', encoding='utf-8') as f1:
                f1.write('')
            self.console_signal.emit('已检测到新版本:%s，正在下载更新，预计耗时3分钟，请稍等......' % self.new_version, 'lime')
            r = requests.get(self.zip_url, stream=True)
            downloaded = 0
            isoutprint = 0
            f = open(self.zip_file, "wb")
            for data in r.iter_content(chunk_size=512):
                downloaded += len(data)
                if (downloaded - isoutprint) > 1000000:  # 如果下载大小大于1MB输出打印一次提示
                    isoutprint = downloaded
                    self.console_signal.emit(
                        '当前下载大小:%s MB' % (Decimal(downloaded / 1000000).to_integral()), 'orange')
                if data:
                    f.write(data)
            f.close()
            time.sleep(3)
            fz = zipfile.ZipFile(self.zip_file, 'r')
            for file in fz.namelist(): fz.extract(file, self.version_path)
            fz.close()
            zip_file = zipfile.ZipFile(self.zip_file2)
            for names in zip_file.namelist(): zip_file.extract(names, self.version_path2)  # 双层目录解压
            zip_file.close()
            self.console_signal.emit('已下载到新版本，重新关闭打开工具则自动更新', 'lime')
        else:
            self.console_signal.emit('已是最新版本，无需更新', 'lime')
        try:
            os.remove(self.zip_file)
            shutil.rmtree('C:/TestTime/2/sztangwang-main')
        except:
            pass
