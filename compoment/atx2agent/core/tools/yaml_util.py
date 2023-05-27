import json
import os.path
import threading

import yaml

get_object_path = os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

# 读取yaml
def read_test_yaml(file):
    with open(get_object_path+file,mode='r',encoding='utf-8') as f:
        result = yaml.load(stream=f,Loader=yaml.FullLoader)
        return result

def read_device_task(file):
    with open(get_object_path + file, mode='r', encoding="utf-8") as f:
        data = yaml.load(stream=f, Loader=yaml.FullLoader)
        if data:
            return data
        else:
            return None

def write_test_yaml(file,data):
    with open(get_object_path+file,mode='w',encoding='utf-8') as f:
        yaml.dump(data,f,allow_unicode=True)

def clear_test_yaml(file):
    with open(get_object_path+file,mode='w',encoding='utf-8') as f:
       f.truncate()

class YamlUtil:
    def __init__(self):
        self.lock = threading.Lock

    def write_test_yaml(self,file, data):
        with self.lock:
            with open(get_object_path + file, mode='w', encoding='utf-8') as f:
                yaml.dump(data, f, allow_unicode=True)

if __name__ == '__main__':
    result = read_test_yaml(r'\core\testcases\case_demo2.yaml')
  #  D:\python - workspace\ATX\atx2agent\core\testcases
    print(json.dumps(result,ensure_ascii=False))