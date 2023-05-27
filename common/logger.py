import time
import os
import sys
import logging
from logging import handlers

formater = '%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s'

# 路径管理
def log_path_check():
    log_path = os.getcwd() + '/Logs/'
    if not os.path.exists(log_path):
        os.mkdir(log_path)
    day = time.strftime('%Y-%m-%d', time.localtime())
    log_name = log_path + day + '.log'
    return log_name


class Logger(object):
    def __init__(self, filename=log_path_check(), level='warning', when='D', backCount=3,
                 fmt=formater):
        self.level_relations = {
            'debug': logging.DEBUG,
            'info': logging.INFO,
            'warning': logging.WARNING,
            'error': logging.ERROR,
            'crit': logging.CRITICAL
        }  # 日志级别关系映射
        self.logger = logging.getLogger()
        format_str = logging.Formatter(fmt)  # 设置日志格式
        self.logger.setLevel(self.level_relations.get(level))
        

        # 设置日志级别
        if not self.logger.handlers:
            self.sh = logging.StreamHandler()  # 往屏幕上输出
            self.sh.setFormatter(format_str)  # 设置屏幕上显示的格式
            self.th = handlers.TimedRotatingFileHandler(filename=filename, when=when, backupCount=backCount,
                                                   encoding='utf8')  # 往文件里写入#指定间隔时间自动生成文件的处理器
            # 实例化TimedRotatingFileHandler
            # interval是时间间隔，backupCount是备份文件的个数，如果超过这个个数，就会自动删除，when是间隔的时间单位，单位有以下几种：
            # S 秒
            # M 分
            # H 小时、
            # D 天、
            # W 每星期（interval==0时代表星期一）
            # midnight 每天凌晨
            self.th.setFormatter(format_str)  # 设置文件里写入的格式
            self.logger.addHandler(self.sh)  # 把对象加到logger里
            self.logger.addHandler(self.th)
if __name__ == '__main__':
    log = Logger(level="info")
    log.logger.info('error')
