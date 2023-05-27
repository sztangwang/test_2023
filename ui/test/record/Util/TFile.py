# -*-coding:UTF-8-*- #

import os
import re
import sys
import json
import time
import shutil
import datetime
from pathlib import Path



FILE = Path(__file__).resolve()
BASE_PATH = sys.base_prefix
BASE_DIRECTORY = os.path.dirname(BASE_PATH)
LOG_PATH = "%s\Log"%FILE.parents[1]
CONFIG_PATH = "%s\Config"%FILE.parents[1]
FILE_DIR_NAME = os.path.dirname(FILE.parents[0])
FILE_BASE_NAME = os.path.basename(FILE.parents[0])
KEY_PATH = '%s\key\key.json'%CONFIG_PATH
SCRIPT_ID = "UnknownScriptID"
CONFIG_FILE = '%s\\configFile.txt'%CONFIG_PATH

if re.search(r"\w+-\w+-\d{3}", FILE_BASE_NAME): SCRIPT_ID = re.findall(r"\w+-\w+-|\w+-\d{3}", FILE_BASE_NAME)[0]

SCRIPT_FOLDER = "%s%s" % (SCRIPT_ID, time.strftime("%y%m%d-%H%M%S", time.localtime()))
DATE_FORMAT = "%Y/%m/%d %H:%M:%S"
CONFIG_FILE_NAME = 'config.json'

print("python path     = %s" % BASE_PATH)
print("Log path  = %s" % LOG_PATH)
print("Config path = %s" % CONFIG_PATH)
print("Filename        = %s" % FILE.parents[0])
print("File path       = %s" % FILE_DIR_NAME)
print("File basename   = %s" % FILE_BASE_NAME)
print("KEY_PATH   = %s" % KEY_PATH)
is_screenshot = ""

if not os.path.isdir(LOG_PATH):
    try:
        os.makedirs("Log")
    except:
        pass

def set_configs(keyword,keyword2,value, folder_name="Json"):
    try:
        path = get_config_file("config.json")
        with open(path, 'r', encoding="UTF-8") as fp:
            dict_config = json.load(fp)
        if keyword in dict_config.keys():
            dict_config[keyword][keyword2] = value
            with open(path, 'w', encoding="UTF-8") as fp:
                json.dump(dict_config, fp, indent=4, ensure_ascii=False)
            return True
        project = dict_config["Project"]
        client_type = dict_config["ClientType"]
        path = get_config_file("%s/%s/%s.json" % (folder_name, project, client_type))
        with open(path, 'r', encoding="UTF-8") as fp:
            client_type_config = json.load(fp)
        
        client_type_config[keyword][keyword2] = value
        
        with open(path, 'w', encoding="UTF-8") as fp:
            json.dump(client_type_config, fp, indent=4, ensure_ascii=False)
        return True
    except Exception as e:
        print(e)
        return False

def get_scrcpy_path():

    return "%s\\res\scrcpy.exe"%CONFIG_PATH


def get_scrcpy_lib_path():
    
    return "%s\\lib\\"%CONFIG_PATH

def get_scrcpy_icons_path():
    
    return "%s\\icons\\"%CONFIG_PATH

def get_record_file_list():
    path = os.path.abspath(get_record_path())
    return os.listdir(path)

def get_record_path():
    record_path = '%s\\record\\'%CONFIG_PATH
    if not os.path.isdir(os.path.dirname(record_path)):
        os.makedirs(os.path.dirname(record_path))
    return record_path

def set_new_file(filePath):
    with open(filePath, 'wb+'):
        pass

def set_config_file(value,name):
    
    with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
        strs = f.read()
    rgx = re.compile('(?<=%s=).*?(?=#)' % name)
    strs = rgx.sub(str(value), strs)
    with open(CONFIG_FILE, 'w+', encoding='utf-8') as f:
        f.write(strs)


def get_config_value(value):
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            configstr = f.read()
        str = (re.findall(r"%s=(.+?)#"%value, configstr))[0]
    except:
        return ''
    return str



def get_json_list(filepath):
    try:
        with open(filepath, 'r', encoding="UTF-8") as fp:
            dict_keys = json.load(fp)
    except Exception as e:
        return None
    return dict_keys

def get_json_key(keyword,filepath):
    try:
        with open(filepath, 'r', encoding="UTF-8") as fp:
            dict_keys = json.load(fp)
    except Exception as e:
        print(e)
        return None
    if keyword in dict_keys.keys():
        return dict_keys[keyword]
    return None

    

def read_key_list_except(encodings,filepath):
    buttonList = []
    for line in open(filepath, encoding=encodings):
        if line.find('button') != -1:
            button = line.split('=')[-1]
            button = button.replace('\n', '').strip()
            buttonList.append(button)
    return buttonList

def get_datetime(format_str="%m%d%H%M%S.%f"):
   
    return datetime.datetime.now().strftime(format_str)


def get_run_num():
    file = "%s\\num.txt"%CONFIG_PATH 
    with open(file, encoding='utf-8') as f:
        line = f.readlines()
    try:
        strs = line[-1].replace('\n', '')
    except:
        strs = '0'
    if strs is None or strs == '':
        strs = '0'
    with open(file, 'w+') as f:
        f.write(strs + "\n")
    return int(strs)

def set_run_num(text):
    file = "%s\\num.txt"%CONFIG_PATH 
    with open(file, 'w+') as f:
        f.write("{}\n".format(text))






def get_file_size(file_path):
    file_size = os.path.getsize(file_path)
    file_size = file_size / float(1024 * 1024)
    return round(file_size, 3)


def get_cache_file(relative_path):
    relative_path = relative_path.replace("\\", os.sep)
    relative_path = relative_path.replace("/", os.sep)
    path = os.path.join(LOG_PATH, relative_path)
  
    if LOG_PATH in path:
        if not os.path.isdir(os.path.dirname(path)):
            os.makedirs(os.path.dirname(path))
            
        return path
    else:
        return None
    




def get_cache_picture(keyword="", pic_format=".png"):
    relative_path = "%s/Picture/%s%s" % (keyword,get_datetime(format_str="%d_%H%M%S"), pic_format)
    return get_cache_file(relative_path)




def get_cache_video(keyword="", video_format=".mp4"):
    main_version = load_config("MainVersion")
    if keyword == "":
        relative_path = "Data/%s/%s/Video/%s%s" % (main_version, SCRIPT_FOLDER, get_datetime(), video_format)
    else:
        relative_path = "Data/%s/%s/Video/%s/%s%s" % (main_version, SCRIPT_FOLDER, keyword, get_datetime(), video_format)
    path = get_cache_file(relative_path)
    return path


def get_cache_audio(keyword="", audio_format=".wav"):
    main_version = load_config("MainVersion")

    if keyword == "":
        relative_path = "Data/%s/%s/Audio/%s%s" % (main_version, SCRIPT_FOLDER, get_datetime(), audio_format)
    else:
        relative_path = "Data/%s/%s/Audio/%s/%s%s" % \
                        (main_version, SCRIPT_FOLDER, keyword, get_datetime(), audio_format)
    return get_cache_file(relative_path)


def get_cache_serial(keyword=""):
    main_version = load_config("MainVersion")
    if keyword == "":
        relative_path = "Data/%s/%s/serial_%s.log" % (main_version, SCRIPT_FOLDER, get_datetime())
    else:
        relative_path = "Data/%s/%s/%s_serial_%s.log" % (main_version, SCRIPT_FOLDER, keyword, get_datetime())
    return get_cache_file(relative_path)

def get_complete_picture_path(keyword=""):
    main_version = load_config("MainVersion")
    if keyword == "":
        relative_path = "Data/%s/%s/Picture/%s/" % (main_version, SCRIPT_FOLDER,get_datetime(format_str="%Y%m%d"))
    else:
        relative_path = "Data/%s/%s/Picture/%s" % (main_version, SCRIPT_FOLDER, keyword)
    return get_cache_file(relative_path)


def get_config_file(relative_path, check_exists=True):
    relative_path = relative_path.replace("\\", os.sep)
    relative_path = relative_path.replace("/", os.sep)
    path = os.path.join(CONFIG_PATH, relative_path)
    stream_path = os.path.join(CONFIG_PATH, "Stream")
    if os.path.exists(path) or not check_exists or stream_path in path:
        return path
    else:
        return None


def set_json_record(file_name,add_content,is_clean=False):
    filepath = get_record_path() + file_name
    if is_clean:
       with open(filepath, 'wb+') as e:pass

    json_content = get_json_list(filepath)
    if not json_content:
        with open(filepath, 'w', encoding="UTF-8") as f_new:
            json.dump(add_content, f_new)
        return

    json_content.update(add_content)
    with open(filepath, 'w', encoding="UTF-8") as f_new:
        json.dump(json_content, f_new)

def set_config(keyword, value, folder_name="Json"):
    try:
        path = get_config_file(CONFIG_FILE_NAME)
        with open(path, 'r', encoding="UTF-8") as fp:
            dict_config = json.load(fp)
        if keyword in dict_config.keys():
            dict_config[keyword] = value
            with open(path, 'w', encoding="UTF-8") as fp:
                json.dump(dict_config, fp, indent=4, ensure_ascii=False)
            return True
        project = dict_config["Project"]
        client_type = dict_config["ClientType"]
        path = get_config_file("%s/%s/%s.json" % (folder_name, project, client_type))
        with open(path, 'r', encoding="UTF-8") as fp:
            client_type_config = json.load(fp)
        client_type_config[keyword] = value
        with open(path, 'w', encoding="UTF-8") as fp:
            json.dump(client_type_config, fp, indent=4, ensure_ascii=False)
        return True
    except Exception as e:
        print(e)
        return False


def load_config(keyword, folder_name="Json"):
    try:
        path = get_config_file(CONFIG_FILE_NAME)
        with open(path, 'r') as fp:
            dict_config = json.load(fp)
        if keyword in dict_config.keys():
            return dict_config[keyword]
        project = dict_config["Project"]
        client_type = dict_config["ClientType"]
        path = get_config_file("%s/%s/%s.json" % (folder_name, project, client_type))
        with open(path, 'r', encoding="UTF-8") as fp:
            dict_config1 = json.load(fp)
        return dict_config1[keyword]
    except Exception as e:
        print("Exception", e)
        return None


def get_cache_xml(keyword="", file_format=".xml"):
    main_version = load_config("MainVersion")
    if keyword == "":
        relative_path = "Data/%s/%s/XML/%s%s" % (main_version, SCRIPT_FOLDER, get_datetime(), file_format)
    else:
        relative_path = "Data/%s/%s/XML/%s/%s%s" % \
                        (main_version, SCRIPT_FOLDER, keyword, get_datetime(), file_format)
    return get_cache_file(relative_path)







def exists(path):
    return os.path.exists(path)


def remove_file(path):
    return os.remove(path)


def remove_all_file(path=LOG_PATH):
    if os.path.exists(path):
        for file in os.listdir(path):
            filename = os.path.join(path, file)
            if os.path.isdir(filename):
                remove_all_file(filename)
                shutil.rmtree(filename)
            else:
                os.remove(filename)


# #print(get_json_list("D:\pyqt5-master-complete\RunTools\Config\\record\\record_0319154322.json"))
# set_json_record()