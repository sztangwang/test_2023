import asyncio
import json
import multiprocessing
import os
import queue
import subprocess
import threading
from dataclasses import dataclass, field
from enum import Enum
from threading import Event
from queue import Queue
from concurrent.futures import as_completed, ThreadPoolExecutor
import time
from typing import Optional

import pytest
import yaml
from adbutils import adb
from dataclasses_json import dataclass_json
from compoment.atx2agent.core.common.logs.log_uru import Logger
from compoment.atx2agent.core.core_test.test_android import run_test2
from utils.fileutils import load_yaml_data, write_yaml_data, clear_yaml_data, device_status_file, device_list_file, \
    list_json_to_dict, list_class_to_json, dict_list_to_new_dict

get_object_path = os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

file_lock = threading.Lock()

logger = Logger().get_logger

TASK_CASES = []


@dataclass_json
@dataclass
class TaskStatus:
    CREATED = 1  # 任务创建
    RUNNING = 2  # 任务正在执行
    FINISHED = 3  # 任务执行完成
    TIMEOUT = 4  # 任务超时
    ERROR = 5  # 任务执行失败
    CANCELED = 6  # 任务被取消
    STOP = 7  # 任务被停止


@dataclass_json
@dataclass
class TaskType:
    KW_UI_TEST = "KW_UI_TEST"  # UI测试任务
    SMOKE_TEST = "SMOKE_TEST"  # 冒烟测试任务
    HARDWARE_TEST = "HARDWARE_TEST"  # 硬件测试任务
    PO_UI_TEST = "PO_UI_TEST"  # PageObject 模式的UI任务
    NONE = "NONE"  # 无任务


@dataclass_json
@dataclass
class DeviceStatus:
    OFFLINE = "offline"  # 离线
    ONLINE = "online"  # 在线
    IDLE = "idle"  # 空闲
    BUSY = "busy"  # 繁忙
    DEBUGGING = "debugging"  # 调试中
    TESTING = "testing"  # 测试中
    UNKNOWN = "unknown"  # 未知


@dataclass_json
@dataclass
class DeviceType:
    C4701 = "C4701"
    C4702 = "C4702"
    C4703 = "C4703"
    UNKNOWN = "unknown"


def timestamp_to_time(timestamp):
    time_struct = time.localtime(timestamp)
    return time.strftime('%Y-%m-%d %H:%M:%S', time_struct)


def update_device_task(file_path, device, task=None):
    """
    更新设备和任务状态
    @param device:
    @param task:
    @return:
    """
    file_lock.acquire()
    try:
        data = load_yaml_data(file_path)
        # assign_task_to_device(file_path, device, task)
        update_task_device_status(data, device, task)
    finally:
        file_lock.release()


def update_device_list(file_path, devices):
    file_lock.acquire()
    try:
        add_device_list_yaml(file_path, devices)
    finally:
        file_lock.release()


def delete_device_yaml(file_path, device):
    data = load_yaml_data(file_path)
    if device.serial in data["devices"]:
        del data["devices"][device.serial]
        write_yaml_data(file_path, data)


def add_device_list_yaml(file_path, devices_):
    """
    添加设备信息到 device_list.yaml 中
    @param file_path:
    @param device:
    @return:
    """
    devices = load_yaml_data(file_path)

    if not devices:
        devices = {"devices": {}}
    if len(devices_) == 0:
        return
    for device in devices_:
        if device.serial in devices:
            devices["devices"][device.serial]['status'] = device.status
            devices["devices"][device.serial]['ip'] = device.ip
            devices["devices"][device.serial]['device_id'] = device.serial
            devices["devices"][device.serial]['device_type'] = device.device_type
        else:
            devices["devices"][device.serial] = {"device_id": device.serial,
                                                 "device_type": device.device_type,
                                                 "status": device.status,
                                                 "ip": device.ip}
    write_yaml_data(file_path, devices)


def _init_write_task_device(file_path):
    data = {"devices": {}, "tasks": {}}
    write_yaml_data(file_path, data)


def _check_assign_task_device(data, device, task=None):
    if task is None:
        # 说明还没有任务呢，直接跳过
        pass
    else:
        # 获取设备中的任务 然后和任务中的任务进行对比，如果是同一个任务说明已经分配了
        if device.serial not in data["devices"]:
            task.assign_flag = False
            return task.assign_flag
        d_task_id = data["devices"][device.serial]["task_id"]
        t_task_id = data["tasks"][task.task_id]["task_id"]
        device_status = data["devices"][device.serial]["status"]
        task_status = data["tasks"][task.task_id]["status"]
        if d_task_id == t_task_id and d_task_id == task.task_id and device_status == DeviceStatus.BUSY and task_status == TaskStatus.RUNNING:
            logger.info("这个设备[{}]已经分配了任务了执行了.".format(device.serial))
            # # 重置任务状态和设备状态
            # device.set_status(DeviceStatus.BUSY)
            # task.update_status(TaskStatus.RUNNING)
            task.assign_flag = True
            return task.assign_flag
        else:
            task.assign_flag = False
            return task.assign_flag


def assign_task_to_device(file_path, device, task=None):
    """
    分配任务到设备，并检查任务是否已经被分配执行了.
    @param file_path:
    @param device:
    @param task:
    @return:
    """
    d = load_yaml_data(file_path)
    if d is None:
        # 先初始化任务和设备yaml
        _init_write_task_device(device_status_file)
    data = load_yaml_data(file_path)
    return _check_assign_task_device(data, device, task)


def update_task_device_status(data, device, task=None):
    """
    更新设备和任务的状态
    @param data:
    @param device:
    @param task:
    @return:
    """
    if device.serial in data["devices"]:
        current_task = data["devices"][device.serial]["task_id"]
        # 如果是同一个任务则进行任务的状态修改
        if current_task == task.task_id:
            data["devices"][device.serial]["status"] = device.status
            data["devices"][device.serial]["task_id"] = task.task_id
            data["devices"][device.serial]["device_id"] = device.serial
            data["tasks"][current_task]["status"] = task.status
            data["tasks"][current_task]["device_id"] = device.serial
            data["tasks"][current_task]["task_id"] = task.task_id
        else:
            # 如果不同，则判断下是否是设备被占用了，已经绑定了任务了。
            logger.debug("不做处理吧.")
            pass
    else:
        data["devices"][device.serial] = {"status": device.status, "task_id": task.task_id,
                                          "device_id": device.serial}

    if task.task_id in data["tasks"]:
        current_device = data["tasks"][task.task_id]["device_id"]
        if current_device == device.serial:
            data["devices"][current_device]["status"] = device.status
            data["devices"][current_device]["task_id"] = task.task_id
            data["devices"][current_device]["device_id"] = device.serial
            data["tasks"][task.task_id]["status"] = task.status
            data["tasks"][task.task_id]["device_id"] = device.serial
            data["tasks"][task.task_id]["task_id"] = task.task_id
        else:
            logger.debug("不做处理吧.")
            pass
    else:
        data["tasks"][task.task_id] = {"status": device.status, "device_id": device.serial,
                                       "task_id": task.task_id}
    write_yaml_data(device_status_file, data)


class Device:
    def __init__(self, serial, ip=None, device_type=DeviceType.UNKNOWN, status=DeviceStatus.IDLE, info=None, task=None):
        self.device_type = device_type
        self.serial = serial
        self.ip = ip
        self.status = status
        self.lock = threading.Lock()
        self.task = task
        self.info =info

    def set_status(self, status):
        with self.lock:
            self.status = status

    def get_status(self):
        with self.lock:
            return self.status

    def assign_task(self, task):
        self.task = task

    # 设置设备类型
    def set_device_type(self, device_type):
        with self.lock:
            self.device_type = device_type

    # 获取设备类型
    def get_device_type(self):
        with self.lock:
            return self.device_type

    def __str__(self):
        return f"Device: 设备ID：{self.serial},设备ip: {self.ip},设备类型： {self.device_type},设备状态： {self.status}"


class DeviceManager:
    _instance_lock = multiprocessing.Lock()
    _instance = None

    def __new__(cls, *args, **kwargs):
        with cls._instance_lock:
            if not cls._instance:
                cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        self.devices = []

    def get_device_list(self):
        """
        从adb.device_list() 中获取设备，并加入到设备列表中
        @return:
        """
        adb_devices = adb.device_list()
        if len(adb_devices) == 0:
            print("No devices connected")
        return adb_devices

    def get_device_info_by_serial(self, serial, devices):
        """
        根据设备的id 返回设备对象的列表
        @param serial:
        @param devices:
        @return:
        """
        for device in devices:
            if serial == device.serial:
                return device

    def get_device_id(self, device_id=None):
        """
        获取设备的设备id
        @param device_id
        @return:
        """
        devices = self.get_device_list()
        if len(devices) == 0:
            logger.info("没有设备连接.")
            return
        if device_id is None:
            device_ids = [device_id.serial for device_id in devices]
            return device_ids
        for device in devices:
            if device_id == device.serial:
                return device.serial
            else:
                logger.info("设备[{}]不存在.".format(device_id))
                return

    def check_device_status1(self, device_serial, online_list=None, device_list=None, data=None):
        """
        检查设备的状态
        @param device_list:
        @param device_serial:
        @return:
        """
        for index, serials in enumerate(device_serial):
            if serials in data["devices"] and serials not in [device.serial for device in device_list]:
                # 根据yaml中的设备号，重新再加入到设备列表中.
                self._add_device_(device_serial)
                return DeviceStatus.IDLE
            elif serials in online_list and device_serial not in device_list:
                return DeviceStatus.ONLINE
            else:
                return DeviceStatus.OFFLINE

    def _add_device_(self, device_serials):
        for serial in device_serials:
            if serial in [d.serial for d in self.devices]:
                print("已存在了的设备了，不需要新增了.")
            else:
                self.device = Device(serial, self.get_device_ip(serial), DeviceType.UNKNOWN)
                logger.info("设备对象[{}]初始化完成.".format(self.device))
                self.add_device(self.device)

    # self.update_device_status(self.devices, DeviceStatus.IDLE)

    def _add_one_device(self, device_serial):
        """
        新增单个设备
        @param device_serial:
        @return:
        """
        if device_serial in [d.serial for d in self.devices]:
            print("已存在了的设备了，不需要新增了.")
        else:
            self.device = Device(device_serial, self.get_device_ip(device_serial), DeviceType.UNKNOWN)
            logger.info("设备对象[{}]初始化完成.".format(self.device))
            self.add_device(self.device)
            self.update_device_status(self.devices, DeviceStatus.IDLE)

    def _init_add_devices(self, device_serial):
        """
        初始化新增设备
        @param device_serial:
        @return:
        """
        # 新增设备
        self._add_device_(device_serial)
        self.update_device_status(self.devices, DeviceStatus.IDLE)
        # 新增到yaml中
        update_device_list(device_list_file, self.devices)

    def _update_devices_status(self, devices, status):
        """
        更新设备列表中的设备状态
        @param devices:
        @param status:
        @return:
        """
        # 获取设备列表中的设备
        self.update_device_status(devices, status)
        update_device_list(device_list_file, devices)

    def _add_device(self, device_serial, data=None):
        """
        增加设备
        @param d:
        @return:
        """
        if data is None:  # 首次新增
            self._init_add_devices(device_serial)
        else:  # 判断状态,看是否可以新增
            d_serials = data["devices"]
            if [serial for serial in device_serial if serial not in d_serials]:
                print("说明有新的设备还没加到yaml中")
                self._init_add_devices(device_serial)
            # if len(self.devices) == 0:  # 说明在yaml中有数据，但是设备列表对象中没有
            #     self._add_device_(device_serial)
            #     print("这里加了设备之后如果开启另一个进程的话，会导致无法判断设备状态.")
            online_devices = self.get_device_list()
            device_status = self.check_device_status1(device_serial, online_devices, self.devices, data)
            if device_status == DeviceStatus.ONLINE:
                self._init_add_devices(device_serial)
            elif device_status == DeviceStatus.IDLE:
                #  self._update_devices_status(self.devices,DeviceStatus.IDLE)
                logger.info("设备[{}]已存在，不能重复新增".format(device_serial))
            else:
                self._update_devices_status(self.devices, DeviceStatus.OFFLINE)
                # TODO 从列表中移除，并且也从yaml中移除到相应的设备
                # 从设备对象列表中移除设备
                for device in self.devices:
                    self.remove_device(device)
                    delete_device_yaml(device_list_file, device)
                    logger.info("设备[{}]不在线，不能新增.".format(self.devices))

    def add_device_(self, d=None):
        data = load_yaml_data(device_list_file)
        device_serial = self.get_device_id(d)
        self._add_device(device_serial, data)

        # data = load_yaml_data(device_list_file)
        # device_serial = self.get_device_id(d)
        # if data is None and self.devices is None:  # 说明是首次，则直接新增设备到列表和yaml中
        #     self._add_device(device_serial)
        # else:
        #     self._add_device(device_serial,data)

    def add_device(self, device: Device):
        self.devices.append(device)

    def remove_device(self, device: Device):
        self.devices.remove(device)

    def is_online(self, device: Device):
        output = subprocess.run(["adb", "devices"], stdout=subprocess.PIPE).stdout.decode("utf-8")
        return device.serial in output

    def get_available_devices(self, status=DeviceStatus.IDLE):
        """根据设备的状态筛选设备"""
        return [device for device in self.devices if device.status == status]

    def release_devices(self, test):
        """释放测试完成后使用的设备"""
        for device in test.devices:
            self.update_device_status(device, DeviceStatus.IDLE)
        test.clear_devices()

    def assign_devices(self, test, num_devices):
        """为测试分配设备"""
        available_devices = self.get_available_devices()
        if len(available_devices) < num_devices:
            logger.error("Not enough available devices")
            raise Exception("Not enough available devices")
        for i in range(num_devices):
            device = available_devices[i]
            self.update_device_status(device, DeviceStatus.BUSY)
            test.add_device(device)

    def get_device_ip(self, device_id):
        # 使用 adb shell ip route 命令查询设备的 IP 地址
        output = subprocess.run(["adb", "-s", device_id, "shell", "ip", "route"], stdout=subprocess.PIPE).stdout.decode(
            "utf-8")
        if output == "":
            return None
        # 解析输出的字符串，获取设备的 IP 地址
        ip = output.split("src ")[1].split(" ")[0]
        return ip

    def get_idle_device_count(self):
        """获取设备列表中空闲设备的数量"""
        idle_count = 0
        for device in self.devices:
            if device.status == DeviceStatus.IDLE:
                idle_count += 1
        return idle_count

    def get_idle_device(self):
        """获取设备列表中的空闲设备"""
        for device in self.devices:
            if device.status == DeviceStatus.IDLE:
                return device
        return None

    def has_device(self, device: Device):
        """查询某个设备是否存在于设备列表中"""
        return device in self.devices

    def has_device_id(self, device_id):
        """
        查询某个设备的id 是否存在于设备列表中
        @param device_id:
        @return:
        """
        for device in self.devices:
            if device.serial == device_id:
                return True
            else:
                return False

    # 获取设备状态
    def get_device_status(self, device: Device):
        return device.get_status()

    def get_device_count(self):
        """获取设备列表中的设备数量"""
        return len(self.devices)

    def get_device_by_id(self, device_id):
        """根据设备 ID 查询设备信息"""
        for device in self.devices:
            if device.serial == device_id:
                return device
        return None

    def update_device_status(self, devices, status):
        """更新设备状态"""
        for device in devices:
            device.set_status(status)

    def check_device_status(self, seconds):
        """检查设备状态"""
        while True:
            if self.get_device_count() == 0:
                logger.debug("No devices connected...")
                return
            for device in self.devices:
                logger.debug("设备[{0}]".format(device))
            time.sleep(seconds)


class Task:
    def __init__(self, name, task_id=None, d: Device = None, task_type=TaskType.NONE, cases=None,
                 timeout=10, task_func=None, *args,
                 **kwargs):
        self.task_id = task_id
        self.name = name
        self.timeout = timeout
        self.start_time = time.time()
        self.end_time = time.time()
        self.task_func = task_func
        self.args = args
        self.kwargs = kwargs
        self.status = TaskStatus.CREATED  # 初始化任创建时，状态为created
        self.task_type = task_type
        self.result = None
        self.device = d  # 任务执行的设备
        self.lock = threading.Lock()
        self.assign_flag = False
        self.cases = cases

    def __str__(self):
        return f"Task: 任务ID:{self.task_id},任务名称：{self.name},任务状态：{self.status}," \
               f"任务所属设备：{self.device}"

    def set_func(self, task_func, *args, **kwargs):
        self.task_func = task_func
        self.args = args
        self.kwargs = kwargs

    # 设置任务ID
    def set_taskid(self, task):
        self.task_id = task.task_id

    def update_status(self, status):
        self.status = status

    def assign_device(self, device):
        """
        将设备分配给当前任务
        @param device:
        @return:
        """
        self.device = device
        device.assign_task(self)

    def run(self, task=None, device=None):
        # device_task = load_yaml_data(device_status_file)
        # if device_task is not None:
        #     if task.task_id is not None and device.serial is not None:
        #         if device_task["tasks"][task.task_id]["device_id"] == device_task["devices"][device.serial]["device_id"]:
        #             device_status = device_task.get('devices').get(device.serial).get("status")
        #             task_status = device_task.get("tasks").get(task.task_id).get("status")
        #             device_serial = device_task.get('devices').get(device.serial).get("device_id")  # 获取设备的id
        #             t_id = device_task.get('tasks').get(task.task_id).get("task_id")  # 获取任务的id
        #             t_d_serial = device_task.get('tasks').get(task.task_id).get("device_id")  # 获取任务中设备的id
        #             self._run_task(device,task)
        #         else:
        #             logger.info("任务和设备执行的不一致，不能执行任务")
        #     else:
        #         logger.info("任务或设备没有找到，无法执行.")
        # else:
        self._run_task(device, task)

    def _run_task(self, device, task):
        device_status = device.status
        task_status = task.status
        if device_status == DeviceStatus.BUSY and task_status == TaskStatus.RUNNING:
            logger.info("设备繁忙，或者任务正在运行，不能执行任务.")
            exit(1)
        # if device_serial == t_d_serial and task.task_id == t_id:
        if task.device.serial == device.serial:
            # if device.device_type.name == DeviceType.UNKNOWN.name:
            #     logger.error("设备类型未知，请指定设备类型")
            #     return None
            if task.task_type == TaskType.NONE:
                logger.error("任务类型未知，请指定任务类型")
                return None
            if device_status == DeviceStatus.OFFLINE:
                logger.error(f"设备", device.serial, "离线了，不能执行测试任务")
                return None
            if device_status == DeviceStatus.TESTING:
                logger.error("设备 [{}] 正在测试中，不能执行测试任务".format(device.serial))
                return None
            if device_status == DeviceStatus.BUSY:
                logger.error("设备 [{}]  繁忙，不能执行测试任务".format(device.serial))
                return None
            if device_status == DeviceStatus.IDLE:
                logger.info("设备 [{}]  空闲，可以执行测试任务".format(device.serial))
                # 根据任务的类型，执行不同的任务
                if task.task_type == TaskType.KW_UI_TEST:
                    # if device.device_type.name != DeviceType.C4701.name and device.device_type.name != DeviceType.C4703.name:
                    #     logger.error("设备类型错误，无法执行UI自动化用例.")
                    # return
                    logger.info("UI test task")
                    # 将json 转换为dict
                    case_json = list_class_to_json(task.cases)
                    cases_dict = dict_list_to_new_dict(list_json_to_dict(case_json))
                    print("cases_dict-------->", cases_dict)
                    task.set_func(run_test2, device, cases_dict, )  # 添加关键字执行函数.
                    return self._run(task, device)
                elif self.task_type == TaskType.SMOKE_TEST:
                    # if device.device_type.name != DeviceType.C4701.name:
                    #     print("设备类型错误，无法执行UI自动化用例.")
                    return self._run(task, device)
                elif self.task_type == TaskType.HARDWARE_TEST:
                    logger.info("Hardware test task")
                    return self._run(task, device)
                elif self.task_type == TaskType.PO_UI_TEST:
                    logger.info("PO test task")
                    # task.set_func(run_test2, device, cases_dict, )  # 设置执行的函数
                    task.set_func(run_po_case, device, task.cases, )
                    return self._run(task, device)
            else:
                logger.error(f"设备", device.serial, "未知状态.")
                logger.debug("No task")
        else:
            logger.info("任务和对应的设备不一致，不能执行任务")
            self.cancel(task)  # 取消这个任务
            exit(1)

    def _run(self, task=None, device=None):
        self.start_time = time.time()
        with self.lock:
            try:
                self.status = TaskStatus.RUNNING
                self.device.set_status(DeviceStatus.BUSY)
                # update_device_task(device_status_file, device, task)  # 更新设备和任务的状态
                msg = self.task_func(*self.args, **self.kwargs)
                self.end_time = time.time()
                if self.end_time - self.start_time > self.timeout:
                    self.task_timeout(task)
                else:
                    self.complete(task)
                time.sleep(1)
                return msg
            except Exception as e:
                print(e)
                self.fail(task)

    def complete(self, task=None):
        self.end_time = time.time()
        #  self.stop_event.set()
        self.status = TaskStatus.FINISHED
        self.device.set_status(DeviceStatus.IDLE)
        # update_device_task(device_status_file, self.device, task)  # 更新设备和任务的状态
        # clear_yaml_data(device_list_file)  # 清空设备信息
        logger.debug("Task {} completed".format(self.name))

    def task_timeout(self, task=None):
        self.end_time = time.time()
        #  self.stop_event.set()
        self.status = TaskStatus.TIMEOUT
        self.device.set_status(DeviceStatus.IDLE)
        # update_device_task(device_status_file, self.device, task)  # 更新设备和任务的状态
        clear_yaml_data(device_list_file)  # 清空设备信息
        if task:
            logger.debug("Task {} timeout".format(task.name))
            # 抛出超时异常
            raise TimeoutError("Task {} timeout".format(task.name))

    def fail(self, task=None):
        self.end_time = time.time()
        # self.stop_event.set()
        self.status = TaskStatus.ERROR
        self.device.set_status(DeviceStatus.IDLE)
        # update_device_task(device_status_file, self.device, task)  # 更新设备和任务的状态
        clear_yaml_data(device_list_file)  # 清空设备信息
        logger.debug("Task {} failed".format(self.name))
        # 抛出异常
        raise Exception("Task {} failed".format(self.name))

    def cancel(self, task=None):
        self.end_time = time.time()
        # self.stop_event.set()
        self.status = TaskStatus.CANCELED
        self.device.set_status(DeviceStatus.IDLE)
        # update_device_task(device_status_file, self.device, task)  # 更新设备和任务的状态
        clear_yaml_data(device_list_file)  # 清空设备信息
        logger.debug("Task {} canceled".format(self.name))

    # 停止任务
    def stop(self, task=None):
        self.end_time = time.time()
        # self.stop_event.set()
        self.status = TaskStatus.STOP
        self.device.set_status(DeviceStatus.IDLE)
        # update_device_task(device_status_file, self.device, task)  # 更新设备和任务的状态
        clear_yaml_data(device_list_file)  # 清空设备信息
        logger.debug("Task {} stopped".format(self.name))


@dataclass_json
@dataclass
class TaskResult:
    task_name: str = None  # 任务对象 ,包括任务类型，任务名称，任务状态
    status: Optional[TaskStatus] = 0  # 任务执行结果 0: 成功 1: 失败, 2: 超时, 3: 取消, 4: 暂停, 5: 停止
    time: Optional[str] = None  # 任务执行时间
    error: Optional[str] = None  # 任务执行错误信息
    start_time: Optional[str] = None  # 任务执行开始时间
    end_time: Optional[str] = None  # 任务执行结束时间
    message: Optional[str] = None  # 任务执行信息
    device_status: Optional[DeviceStatus] = None  # 设备状态


@dataclass_json
@dataclass
class TaskDevice:
    task: Task
    device: Device
    #  初始化一个默认的停止事件对象
    stop_event: threading.Event = field(default_factory=threading.Event)


class TaskManager:
    def __init__(self, max_workers=2):
        self.task_queue = Queue()
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.stop_event = Event()
        self.tasks = []  # 任务列表
        self.devices = None  # 设备列表
        self.device_tasks = []  # 保存任务和设备
        self.task_manager_lock = threading.Lock()
        self.new_devices = None  # 新的设备列表
        self.task_device_list = []
        self.tasks_running = []

    # 设置新的设备
    def set_new_devices(self, new_devices):
        self.new_devices = new_devices

    def add_task(self, task):
        # 判断哪个任务被占用了，只将这个任务排除掉
        if task.assign_flag:
            return
        self.task_queue.put(task)
        task_num = self.task_queue.qsize()
        logger.debug("Task queue size: {}".format(task_num))
        self.tasks.append(task)

    def add_task_device(self, task_device):
        """
        添加设备和任务
        @param task_device:
        @return:
        """
        self.task_queue.put(task_device)
        task_num = self.task_queue.qsize()
        logger.debug("Task queue size: {}".format(task_num))
        self.task_device_list.append(task_device)

    def get_device_by_status(self, status):
        """
        从设备列表中获取设备
        @param status:
        @return:
        """
        result = []
        for device in self.devices:
            if device.status == status:
                result.append(device)
        return result

    def add_devices(self):
        device_manager = DeviceManager()
        device_manager.add_device_()
        # 获取所有的设备
        devices = device_manager.devices  # 这里获取的是真正的设备
        self.devices = devices

    def get_devices(self):
        return self.devices

    def get_task_by_task_id(self, task_id, tasks):
        """
        根据任务id,查询列表中的任务
        @param task_id:
        @param tasks:
        @return:
        """
        for task in tasks:
            if task_id == task.task_id:
                return task
        return None

    def dynamic_assign_device_to_task(self, file_path, devices, tasks):
        """
        动态分配空闲的设备给任务
        @param devices # 空闲的设备列表
        @param tasks  # 任务列表
        @return:
        """
        idle_devices = [device for device in devices if device.task is None]
        idle_task = [task for task in tasks if task.device is None]

        for device, task in zip(idle_devices, idle_task):
            if assign_task_to_device(file_path, device, task):
                print("任务已经分配执行了.就别再分配了.")
            else:
                update_device_task(file_path, device, task)
                task.assign_device(device)  # 给任务分配设备

        # for device in devices:
        #     for task in tasks:
        #         if device.status.name == DeviceStatus.IDLE.name and task.status.name ==TaskStatus.CREATED.name:
        #             self.assign_task_to_device(file_path,device,task)
        #             break

    def dynamic_assign_device_to_task1(self, file_path, task_device_list):
        """
        动态分配空闲的设备给任务
        @param devices # 空闲的设备列表
        @param tasks  # 任务列表
        @return:
        """
        idle_devices = [task_device.device for task_device in task_device_list if task_device.device.task is None]
        idle_task = [task_device.task for task_device in task_device_list if task_device.task.device is None]
        for device, task in zip(idle_devices, idle_task):
            if assign_task_to_device(file_path, device, task):
                print("任务已经分配执行了.就别再分配了.")
            else:
                update_device_task(file_path, device, task)
                task.assign_device(device)  # 给任务分配设备

    @staticmethod
    def get_task_status(task):
        while True:
            print(f"task_name -> {task.name} ,task status -> {task.get_status(task)}")
            time.sleep(1)

    # 删除任务
    def delete_task(self, task):
        print("delete task: ", task)
        self.tasks.remove(task)
        self.task_queue.task_done()

    # 设置任务的结果
    @staticmethod
    def set_task_result(task, result):
        task.result = result

    # 获取任务的结果
    @staticmethod
    def get_task_result(task):
        if task:
            return task.result
        else:
            return "No task"

    def task_done(self, task, task_result):
        if task:
            task_r = TaskResult(task_name=task.name, status=task.status, device_status=task.device.status,
                                time=round(task.end_time - task.start_time, 0),
                                start_time=timestamp_to_time(task.start_time),
                                end_time=timestamp_to_time(task.end_time))
        else:
            task_r = TaskResult(task_name="None", status=TaskStatus.ERROR, device_status=DeviceStatus.IDLE,
                                time='0', start_time=None, end_time=None)
        # 根据任务的执行状态，设置任务的结果
        if task.status == TaskStatus.FINISHED:
            task_r.message = "Task {} completed TaskMessage: {}".format(task.name, task_result)
            self.set_task_result(task, task_r)
        elif task.status == TaskStatus.TIMEOUT:
            task_r.message = "Task {} timeout".format(task.name)
            self.set_task_result(task, task_r)
        elif task.status == TaskStatus.ERROR:
            task_r.message = "Task {} failed ".format(task.name)
            task_r.error = task_result
            self.set_task_result(task, task_r)
        elif task.status == TaskStatus.CANCELED:
            task_r.message = "Task {} canceled".format(task.name)
            self.set_task_result(task, task_r)
        elif task.status == TaskStatus.STOP:
            task_r.message = "Task {} stopped".format(task.name)
            self.set_task_result(task, task_r)

        # self.stop_event.set()
        self.task_queue.task_done()

    def start(self):
        task = None
        while not self.stop_event.is_set():
            try:
                task = self.task_queue.get(timeout=500)
            except Exception as e:
                logger.error(e)
                break
            task.stop_event.clear()
            with self.executor as executor:
                devices = self.get_device_by_status(DeviceStatus.IDLE)
                data = load_yaml_data(device_status_file)
                # 如果self.tasks 中的task的task_id 在 yaml文件中 tasks 中，则使用这个task
                # 如果devices 中的device 在yaml文件中的devices中，则使用这个device
                # 如果data 不为空，那么说明是有设备存在的，如果devices为空说明没有加到这个集合中，则将data中的设备加到devices中。
                # TODO 这里还需要再修改下
                devices_ = [device for device in devices if device.serial in data["devices"]]
                tasks = [task for task in self.tasks if task.task_id in data["tasks"]]
                if len(devices_) == 0:
                    logger.error("无可用的设备，设备可能占用或者设备为空!")
                    return
                if len(tasks) == 0:
                    logger.error("任务为空或者任务繁忙！")
                    return
                for device, task in zip(devices, tasks):
                    task.assign_device(device)  # 给任务分配设备
                task_futures = [executor.submit(task.run, task, device) for device, task in zip(devices, tasks)]
                for future in as_completed(task_futures):
                    try:
                        new_task_ = self.tasks[task_futures.index(future)]
                        new_task = new_task_.task
                        if new_task.status == TaskStatus.STOP.name:
                            if future.cancel():
                                logger.info("Task {} stop".format(new_task.name))
                                self.task_done(new_task, "Task {} stop".format(new_task.name))
                                break
                            else:
                                # 任务停止失败了，已经在执行的任务，无法停止
                                logger.info("Task {} stop failed".format(new_task.name))
                                self.task_done(new_task, "Task {} stop fail".format(new_task.name))
                        if future.done:
                            self.task_done(new_task, future.result())
                    except Exception as e:
                        self.task_done(task, e)
                        logger.error("error{}{}".format(task, e))
                        raise Exception(e)
        else:
            self.stop_shutdown(task)

    def callback(self, future, task):
        """
        获取future的执行结果
        @param future:
        @return:
        """
        if future.done:
            self.task_done(task, future.result())

    def start_task_device(self, callback=None, *callback_args):
        while not self.stop_event.is_set() or not self.task_queue.empty():
            try:
                task_device = self.task_queue.get(timeout=500)
                print("获取到task_device------------>", task_device)
            except Exception as e:
                logger.error(e)
                break
            with self.executor as executor:
                data = load_yaml_data(device_status_file)
                # devices = self.get_device_by_status(DeviceStatus.IDLE)
                # 从队列中取出设备和对应的任务
                task = task_device.task
                device = task_device.device
                if device is None:
                    logger.error("无可用的设备，设备为空!")
                    return
                if task is None:
                    logger.error("任务为空！")
                    return
                task.assign_device(device)  # 给任务分配设备
                task_futures = [executor.submit(task.run, task, device)]
            #  self.stop_event.clear()
            #   for future in as_completed(task_futures):
            #       try:
            #           # 重置任务状态
            #           new_task_ = self.task_device_list[task_futures.index(future)]
            #           new_task = new_task_.task
            #           if new_task.status == TaskStatus.STOP:
            #               if future.cancel():
            #                   logger.info("Task {} stop".format(new_task.name))
            #                   self.task_done(new_task, "Task {} stop".format(new_task.name))
            #                   break
            #               else:
            #                   # 任务停止失败了，已经在执行的任务，无法停止
            #                   logger.info("Task {} stop failed".format(new_task.name))
            #                   self.task_done(new_task, "Task {} stop fail".format(new_task.name))
            #           # if future.done:
            #           #     self.task_done(new_task, future.result())
            #           else:
            #               self.tasks_running.append((new_task, future))
            #       except Exception as e:
            #           self.task_done(task, e)
            #           logger.error("error{}{}".format(task, e))
            #           raise Exception("e")

            # 停止任务的执行
            # for task,future in self.tasks_running:
            #     future.cancel()
            #     self.task_done(task,"Task{} canceled".format(task.name))
            # self.tasks_running.clear()
            # for future in task_futures:
            #     try:
            #         future.add_done_callback(lambda future,task=task:callback(future,task,*callback_args))
            #         if task.status == TaskStatus.STOP.name:
            #             if future.cancel():
            #                 logger.info("Task {} stop".format(task.name))
            #                 self.task_done(task, "Task {} stop".format(task.name))
            #                 break
            #             else:
            #                 logger.info("Task {} stop failed".format(task.name))
            #                 self.task_done(task, "Task {} stop fail".format(task.name))
            #         else:
            #             self.tasks_running.append((task,future))
            #     except Exception as e:
            #         self.task_done(task, e)
            #         logger.error("error{}{}".format(task,e))
            #         self.stop_shutdown(task)
            #         raise Exception(e)

            #     # 串行执行

        # else:
        #     self.stop_shutdown(task)

    # 取消任务
    @staticmethod
    def cancel(task):
        task.cancel()

    @staticmethod
    def stop(task):
        task.stop()

    def stop_shutdown(self, task):
        task.stop_event.set()
        self.executor.shutdown(wait=True)

    def stop(self):
        self.stop_event.set()

    def cancel_task(self, task):
        for t, f in self.tasks_running:
            if t == task:
                f.cancel()
                self.tasks_running.remove((t, f))
                self.task_done(task, "Task{} canceled".format(task.name))
                break

    def get_running_task(self):
        return [t[0] for t in self.tasks_running]

    def mark_task_done(self, task):
        for t, f in self.tasks_running:
            if t == task:
                self.tasks_running.remove((t, f))
                self.task_done(task, "Task {} done".format(task.name))
                break


def task_func_1(*args, **kwargs):
    print("Task 1 is running with args:{} and kwargs:{}".format(args, kwargs))
    time.sleep(15)
    return "Task 1 is done"


def task_func_2(*args, **kwargs):
    print("Task 2 is running with args:{} and kwargs:{}".format(args, kwargs))
    time.sleep(6)
    return "Task 2 is done"


def run_po_case(device, cases):
    if len(cases) > 0:
        case_list = [case_list for case_list in cases if case_list is not None]
     #   case_list =["D:\\python-workspace\\Windows_Agent\\compoment\\atx2agent\\core\\po_testcase\\bt_cases\\test_bt_case.py"]
        # logger.info("case_list={0},device={1}".format(case_list, device))
        c =  case_list
        args = ['-s', '-v', '-q', '--alluredir=result', '--clean-alluredir',
                '--device={}'.format(device.serial)] + c
        logger.info("args================================{0}".format(args))
        # '--alluredir=result', '--clean-alluredir'
        pytest.main(args)


if __name__ == "__main__":
    d = load_yaml_data(device_status_file)
    # if d is None:
    #     # 先初始化任务和设备yaml
    #     _init_write_task_device(device_status_file)
    logger.debug("读取yaml中的数据：：：：：：：：：：：：：".format(d))
    # 创建任务管理器
    manager = TaskManager(6)
    # 创建设备管理器
    device_manager = DeviceManager()
    manager.add_devices()

    # # 开启一个进程来执行检查设备状态的任务,每隔1秒检查一次设备运行状态
    t = threading.Thread(target=device_manager.check_device_status, args=(1,))
    t.start()

    # 获取空闲设备
    idle_devices = manager.get_device_by_status(DeviceStatus.IDLE)
    # 设置设备的类型，每个设备的类型可能不同的，自己设置 ，设置好类型后，将设备和任务进行绑定，或者给设备分配任务

    task_1 = Task(name="task_1", task_id="1111", d=None, task_type=TaskType.KW_UI_TEST, timeout=30,
                  func=task_func_1, args=("arg1", "arg2"),
                  kwargs={"key1": "value1", "key2": "value2"})

    task_2 = Task(name="task_2", task_id="2222", d=None, task_type=TaskType.KW_UI_TEST, timeout=30,
                  func=task_func_1, args=("arg1", "arg2"),
                  kwargs={"key1": "value1", "key2": "value2"})

    manager.add_task(task_1)
    manager.add_task(task_2)

    manager.dynamic_assign_device_to_task(device_status_file, idle_devices, manager.tasks)

    # task = Task("Test task", task_type=TaskType.UI_TEST, timeout=5, func=task_func_1, args=(1, 2, 3),
    #             kwargs={"a": 1, "b": 2})
    # task1 = Task("Test task1", task_type=TaskType.UI_TEST, timeout=7, func=task_func_2, args=(1, 4, 7),
    #              kwargs={"a": 77, "b": 25})
    # task2 = Task("Test task2", task_type=TaskType.SMOKE_TEST, timeout=7, func=task_func_1, args=(1, 55, 34),
    #              kwargs={"a": 14, "b": 244})
    # task3 = Task("Test task3", task_type=TaskType.HARDWARE_TEST, timeout=7, func=task_func_2, args=(1, 45, 74),
    #              kwargs={"a": 427, "b": 255})
    # task4 = Task("Test task4", task_type=TaskType.HARDWARE_TEST, timeout=7, func=task_func_3, args=(1, 425, 74),
    #              kwargs={"a": 427, "b": 255})
    # task5 = Task("Test task5", task_type=TaskType.HARDWARE_TEST, timeout=7, func=task_func_4, args=(1, 22, 223),
    #              kwargs={"a": 4327, "b": 2554})
    # task6 = Task("Test task6", task_type=TaskType.HARDWARE_TEST, timeout=7, func=task_func_5, args=(21, 322, 2234),
    #              kwargs={"a": 43247, "b": 25544})
    # # 添加任务
    # manager.add_task(task)
    # manager.add_task(task1)
    # manager.add_task(task2)
    # manager.add_task(task3)
    # manager.add_task(task4)
    # manager.add_task(task5)
    # manager.add_task(task6)
    # # 取消任务
    # manager.cancel(task5)
    #
    # # 停止任务
    # manager.stop(task6)
    #
    # # # 每隔1秒检查任务状态
    # # t = threading.Thread(target=manager.get_task_status, args=(task,))
    # # t.start()
    # # t1 = threading.Thread(target=manager.get_task_status, args=(task1,))
    # # t1.start()
    # # t2 = threading.Thread(target=manager.get_task_status, args=(task2,))
    # # t2.start()
    # # t3 = threading.Thread(target=manager.get_task_status, args=(task3,))
    # # t3.start()

    # 启动任务管理器
    manager.start()
    # 获取任务的执行结果
    print(manager.get_task_result(task_1))
    print(manager.get_task_result(task_2))

    # print(manager.get_task_result(task))
    # print(manager.get_task_result(task1))
    # print(manager.get_task_result(task2))
    # print(manager.get_task_result(task3))
    # print(manager.get_task_result(task4))
    # print(manager.get_task_result(task5))
    # print(manager.get_task_result(task6))
