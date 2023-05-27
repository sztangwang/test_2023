import datetime
import os
from functools import wraps
import loguru

# 单例类的装饰器
def singleton_class_decorator(cls):
    """
    装饰器，单例类的装饰器
    """
    # 在装饰器里定义一个字典，用来存放类的实例。
    _instance = {}

    # 装饰器，被装饰的类
    @wraps(cls)
    def wrapper_class(*args, **kwargs):
        # 判断，类实例不在类实例的字典里，就重新创建类实例
        if cls not in _instance:
            # 将新创建的类实例，存入到实例字典中
            _instance[cls] = cls(*args, **kwargs)
        # 如果实例字典中，存在类实例，直接取出返回类实例
        return _instance[cls]

    # 返回，装饰器中，被装饰的类函数
    return wrapper_class

@singleton_class_decorator
class Logger:
    def __init__(self):
        self.logger_add()
        self.logger_add_err()

    def get_project_path(self, project_path=None):
        if project_path is None:
            # 当前项目文件的，绝对真实路径
            # 路径，一个点代表当前目录，两个点代表当前目录的上级目录
            project_path = os.path.realpath('..')
        # 返回当前项目路径
        return project_path

    def get_log_path(self,project_log_filename=None):
        # 项目目录
        project_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # self.get_project_path()
        # 项目日志目录
        project_log_dir = os.path.join(project_path, 'logs/log')
        # 日志文件名
        project_log_filename = project_log_filename  #
        # 日志文件路径
        project_log_path = os.path.join(project_log_dir, project_log_filename)

        # 返回日志路径
        return project_log_path


    def logger_add(self):
        project_log_filename = 'runtime_{}.log'.format(datetime.date.today())
        loguru.logger.add(
            # 水槽，分流器，可以用来输入路径
            sink=self.get_log_path(project_log_filename),
            # 日志创建周期
            rotation='00:00',
            # 保存
            retention='5 day',
            # 文件的压缩格式
            compression='zip',
            # 编码格式
            encoding="utf-8",
            # 具有使日志记录调用非阻塞的优点
            enqueue=True,
            # 按颜色输出
            colorize=True,
            catch=True,
            # 日志级别
            level="INFO",
            serialize=True,
        )

    def logger_add_err(self):
        project_log_filename = 'error_{}.log'.format(datetime.date.today())
        loguru.logger.add(
            # 水槽，分流器，可以用来输入路径
            sink=self.get_log_path(project_log_filename),
            # 日志创建周期
            rotation='00:00',
            # 保存
            retention='5 day',
            # 文件的压缩格式
            compression='zip',
            # 编码格式
            encoding="utf-8",
            # 具有使日志记录调用非阻塞的优点
            enqueue=True,
            # 按颜色输出
            colorize=True,
            catch=True,
            # 日志级别
            level="ERROR",
        )



    @property
    def get_logger(self):
        return loguru.logger

# BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# log_file_path = os.path.join(BASE_DIR, 'Log/my_{time}.log')
# err_log_file_path = os.path.join(BASE_DIR, 'Log/err.log')
# logger.add(sys.stderr, format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name} | {line} | {message}", filter="atx2", level="INFO", encoding='utf-8', enqueue=True,colorize=True,catch=True,retention="5 days")
# logger.add(log_file_path,  format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name} | {line} | {message}", filter="atx2", level="INFO", encoding='utf-8', enqueue=True,colorize=True,catch=True,retention="5 days")
# logger.add(err_log_file_path,  format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name} | {line} | {message}", filter="atx2", level="ERROR", encoding='utf-8', enqueue=True,colorize=True,catch=True,retention="5 days")
