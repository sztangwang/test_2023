import json
import os
import threading

import yaml

from compoment.atx2agent.core.models.model import CaseDto
from res import RESOURCES_DIR

get_object_path = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
file_lock = threading.Lock()

device_status_file = r'\ui\devices\device_task_status.yaml'
device_list_file = r'\ui\devices\device_list.yaml'
device_file_path = r"\ui\devices\device_lists.yaml"


def clear_yaml_data(file_path):
    """
    清空
    @param file_path:
    @return:
    """
    with open(get_object_path + file_path, mode='w', encoding='utf-8') as f:
        f.truncate()


def read_yaml_data(file_path):
    """
    读取yaml 文件中的设备任务数据
    @return:
    """
    with open(get_object_path + file_path, mode='r', encoding="utf-8") as f:
        data = yaml.load(stream=f, Loader=yaml.FullLoader)
        if data:
            return data
        else:
            return None


def write_yaml_data(file_path, data):
    """
    @param data:
    @return:
    """
    with open(get_object_path + file_path, mode='w', encoding='utf-8') as f:
        yaml.dump(data, f, allow_unicode=True)


def load_yaml_data(file_path):
    """
    读取yaml 文件中的设备任务数据
    @return:
    """
    with open(get_object_path + file_path, mode='r', encoding="utf-8") as f:
        data = yaml.load(stream=f, Loader=yaml.FullLoader)
        if data:
            return data
        else:
            return None


def write_case_to_file(cases):
    case_json = list_class_to_json(cases)
    with open("test_case.json", "w") as f:
        json.dump(case_json, f)


def list_class_to_json(list_obj):
    return [e.to_json() for e in list_obj]


# 读取用例
def read_case_from_file():
    with open("test_case.json", "r") as f:
        case_json = json.load(f)
        case_list = list_json_to_class(case_json)
    return case_list


# 将JSON列表转换为对象列表
def list_json_to_class(list_json):
    return [CaseDto.from_json(e) for e in list_json]


# 将dict 做一层处理，组成一个新的dict
def dict_list_to_new_dict(list_dict):
    new_dict = {"cases": []}
    for dict in list_dict:
        new_item = {"case": dict}
        new_dict["cases"].append(new_item)
    return new_dict


# 将json列表 转换为dict 的列表
def list_json_to_dict(list_json):
    return [json_to_dict(e) for e in list_json]


def json_to_dict(json_str):
    return json.loads(json_str)


# 绝对路径转换为相对路径
def get_relative_path(abspath, base_path):
    """
    获取相对路径
    @param path:
    @return:
    """
    rel_path = os.path.relpath(abspath, base_path)
    return rel_path


# 拼接路径和.py文件名
def get_py_path1(abspath, base_path, py_list):
    dir_path = get_relative_path(abspath, base_path)
    new_py_list = []
    for file in py_list:
        file_path = os.path.join(dir_path + "\\", file)
        new_py_list.append(file_path)
    return new_py_list


def get_py_path(abspath, py_list):
    new_py_list = []
    for file in py_list:
        file_path = os.path.join(abspath + "\\", file)
        new_py_list.append(file_path)
    return new_py_list


def getResPath(path: str, fileName: str):
    """
    获取资源文件路径
    """
    return os.path.join(RESOURCES_DIR, path, fileName)


def getWorkingpath(path: str, fileName: str):
    basicpath = './offlinedata'
    path = basicpath + '/' + path + '/' + fileName
    return os.path.abspath(path)


# 读取一个文本文件，然后过滤指定的关键字，如果有符合的关键字，则只将符合关键字所在的行写到新的文件中
def filter_file(file_path, key_word):
    with open(file_path, 'r', encoding="utf-8") as f:
        with open("new_file.txt", "w", encoding="utf-8") as f2:
            f2.truncate()
        for line in f:
            if key_word in line:
                with open("new_file.txt", "a", encoding="utf-8") as f2:
                    f2.write(line)
            else:
                continue


##方法
#     print(os.getcwd())
#     # import os
#     print(os.getcwd())
#     # 获取当前工作目录路径
#     print(os.path.abspath('.'))
#     # 获取当前工作目录路径
#     print(os.path.abspath('./ui/test.txt'))
#     # 获取当前目录文件下的工作目录路径
#     print(os.path.abspath('..'))
#     # 获取当前工作的父目录 ！注意是父目录路径
#     print(os.path.abspath(os.curdir))
#     # 获取当前工作目录路径

if __name__ == '__main__':
    adbspath = "D:\\python-workspace\\Windows_Agent\\compoment\\atx2agent\\core\\po_testcase\\live_cases"
    base_path = 'D:\\python-workspace\\Windows_Agent'
    # 相对路径
    # relative = get_relative_path(adbspath, base_path)

    pylist = ['test_live.py', 'test_live2.py', 'test_live3.py']
    py_path_list = get_py_path(adbspath, pylist)
    print(py_path_list)

    filter_file("./111111.txt", "JDBC")
