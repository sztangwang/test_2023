import time

import pytest
from PyQt5.QtCore import QThread, pyqtSignal
from _pytest import config
from _pytest.config import ExitCode

from compoment.atx2agent.core.common.logs.log_uru import Logger
from ui.test.model.model import TaskStatus, TaskType, Device
from utils.fileutils import list_class_to_json, dict_list_to_new_dict, list_json_to_dict
import ui.test.globalvar  as gl
logger = Logger().get_logger

class TaskManagerThread(QThread):
    update_status_signal = pyqtSignal(int, str)
    update_result_signal = pyqtSignal(int, str)
    # 更新设备的状态
    update_device_status_signal = pyqtSignal(str, int)

    def __init__(self, task, parent=None):
        super(TaskManagerThread, self).__init__(parent)
        self.task = task
        self.start_time = None
        self.end_time = None
        self.task_func = None
        self.args = None
        self.kwargs = None

    def run(self):
       self.clear_result()      # 清空结果
       if self.task.device.connectionState ==Device.BUSY:
           self.update_status_signal.emit(self.task.task_id, TaskStatus.FAILED)
           self.update_result_signal.emit(self.task.task_id, '设备被占用')
           return

       if self.task.device.connectionState == Device.OFFLINE:
            self.update_status_signal.emit(self.task.task_id, TaskStatus.FAILED)
            self.update_result_signal.emit(self.task.task_id, '设备离线了')
            return

       # 根据不同的任务类型，执行不同的任务
       if self.task.task_type == TaskType.KW_UI_TEST:
           case_json = list_class_to_json(self.task.test_cases)
           cases_dict = dict_list_to_new_dict(list_json_to_dict(case_json))
           self.set_func(self.run_kw_ui_test, self.task.device.serialsName, cases_dict,)
           self._run_task()
           return

       elif self.task.task_type == TaskType.PO_UI_TEST:
            self.set_func(self.run_po_case, self.task.device.serialsName, self.task.test_cases,)
            self._run_task()
            return

    def _run_task(self):
        try:
            self.update_status_signal.emit(self.task.task_id, TaskStatus.RUNNING)
            self.start_time = time.time()
            self.update_device_status_signal.emit(self.task.device.serialsName, Device.BUSY)  # 更新设备状态,繁忙
            self.task_func(*self.args,**self.kwargs)  # 执行函数
            self.end_time = time.time()
            if self.end_time - self.start_time > self.task.task_timeout:
                print('超时了')
                self.update_status_signal.emit(self.task.task_id, TaskStatus.TIMEOUT)
                self.update_result_signal.emit(self.task.task_id, '超时了')
                # 更新任务的状态
                self.task.status = TaskStatus.TIMEOUT
            if self.isInterruptionRequested():
                print('被取消了')
                self.update_status_signal.emit(self.task.task_id, TaskStatus.CANCELLED)
                self.update_result_signal.emit(self.task.task_id, '被取消了')
                # 更新任务的状态
                self.task.status = TaskStatus.CANCELLED
            else:
                print('执行完成')
                self.update_status_signal.emit(self.task.task_id, TaskStatus.FINISHED)
                self.update_result_signal.emit(self.task.task_id, '执行成功拉.')
                # 更新任务的状态
                self.task.status = TaskStatus.FINISHED
        except Exception as e:
            logger.error("执行用例失败: {}".format(e))
            self.update_status_signal.emit(self.task.task_id, TaskStatus.FAILED)
            self.update_result_signal.emit(self.task.task_id, '执行失败了')
        finally:
            self.update_device_status_signal.emit(self.task.device.serialsName, Device.IDLE)  # 更新设备状态,空闲


    def task_cancelled(self):
        if self.isRunning():
            self.requestInterruption()
        else:
            self.update_status_signal.emit(self.task.task_id, TaskStatus.CANCELLED)
            self.update_result_signal.emit(self.task.task_id, '被取消了')

    def clear_result(self):
        self.update_result_signal.emit(self.task.task_id, '')

    def set_func(self, task_func, *args, **kwargs):
        self.task_func = task_func
        self.args = args
        self.kwargs = kwargs

    def run_kw_ui_test(self, serial,cases):
            # 将这个cases 保存在全局的变量中，供 pytest 的 fixture 使用
            gl.set_value('kw_cases', cases)
            result = pytest.main(['-vvsqk', 'test_function', '--alluredir=result', '--clean-alluredir',
                         '--cmdopt={}'.format(serial)])
            if result !=ExitCode.OK:
                raise Exception('执行用例失败')


    def run_po_case(self, serial, cases):
        if len(cases) > 0:
            case_list = [case_list for case_list in cases if case_list is not None]
            #   case_list =["D:\\python-workspace\\Windows_Agent\\compoment\\atx2agent\\core\\po_testcase\\bt_cases\\test_bt_case.py"]
            c = case_list
            args = ['-s', '-v', '-q', '--alluredir=result', '--clean-alluredir',
                    '--device={}'.format(serial)] + c
            pytest.main(args)
