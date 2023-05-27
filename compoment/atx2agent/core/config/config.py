import configparser
import json
import os
import yaml

from compoment.atx2agent.core.common.logs.log_uru import Logger

logger = Logger().get_logger


current_path = os.path.dirname(os.path.abspath(__file__))
project_path = os.path.dirname(os.path.abspath(__file__))
info_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'app_info.json')

class YamlConfig:
    # 加载yaml配置文件
    def __init__(self,file_path):
        self.file_path = file_path
        self.config = None
        try:
            if not file_path.endswith((".yml", ".yaml")):
                logger.error(
                    "格式不对，必须指定为[*.yml / *.yaml]的配置文件地址 "
                )
            with open(self.file_path, encoding="utf-8") as fin:
                # 将文件中的内容保存到一个列表中
              #  self.config_list = [line.strip() for line in fin]
                fin.seek(0)
                # 加载配置文件
                self.config = yaml.safe_load(fin)
        except FileNotFoundError:
            logger.error(
                f"找不到此文件 '{self.file_path}'! 再次检查下文件路径. (当前所在目录: '{os.getcwd()}')"
            )

    def get_key_value(self, key):
        """
        获取配置中的值
        :param key: 配置中的key，支持多级，用.分割
        :return: 配置中的值
        """
        value = self.config
        for k in key.split("."):
            value = value[k]
        return value

    # 获取配置文件中 node ，key 的值
    def get_node_key_value(self, node, key):
        # 节点通过.分割
        nodes = node.split(".")
        # 获取配置文件中的值
        config = self.config
        for n in nodes:
            config = config[n]
        return config[key]

    def save(self):
        """将修改后的配置写入文件"""
        with open(self.file_path, "w") as f:
            yaml.dump(self.config, f)

    def set_key_value(self, key, value):
        """
        设置配置中的值
        :param key: 配置中的key，支持多级，用.分割
        :param value: 配置中的值
        """
        config = self.config
        keys = key.split(".")
        for k in keys[:-1]:
            config = config[k]
        config[keys[-1]] = value
        self.save()

    def set_node_key_value(self, node, key, value):
        """
        修改配置文件中的值，指定节点 如果不存在则新增，如果存在则修改
        """
        # 节点通过.分割
        nodes = node.split(".")
        # 获取配置文件中的值
        config = self.config
        for n in nodes:
            # 判断节点是否存在，如果不存在则新增
            if n not in config:
                config[n] = {}
            config = config[n]
        # 判断key是否存在
        if key in config:
            config[key] = value
        else:
            config[key] = value
        # 将修改后的值写入文件
        self.save()



class ReadConfig:
    """
    加载ini配置文件
    """

    def __init__(self, ini_path):
        self.ini_path = ini_path
        if not os.path.exists(ini_path):
            raise FileNotFoundError("Profile %s does not exist！" % ini_path)
        self.config = configparser.RawConfigParser()  # When there are% symbols, use raw to read
        self.config.read(ini_path, encoding='utf-8')

    def _get(self, section, option):
        """

        :param section:
        :param option:
        :return:
        """
        return self.config.get(section, option)

    def _set(self, section, option, value):
        """

        :param section:
        :param option:
        :param value:
        :return:
        """
        self.config.set(section, option, value)
        with open(self.ini_path, 'w') as f:
            self.config.write(f)

    def getvalue(self, env, name):
        """
         # 根据section,option 读取ini文件的值
        :param env:
        :param name:
        :return:
        """
        return self._get(env, name)

    def update_value(self, env, name, value):
        """
         # 根据section,option 修改ini文件的value值
        :param env:
        :param name:
        :param value:
        :return:
        """
        return self._set(env, name, value)


if __name__ == '__main__':
    case_demo= YamlConfig("../../conf.yaml")
    print("case_demo---->>",case_demo.config)
    # 获取值
    print(case_demo.get_key_value("env.test.device_info"))
    # 设置值，如果不存在则新增，如果存在则修改
    case_demo.set_node_key_value("env.test.user_info","xxxxx","xxx2323")
    case_json= json.dumps(case_demo.config,ensure_ascii=False)
    print(case_json)


    #
    # read_=ReadConfig("../../config.ini")
    # print(read_.getvalue("app_info","package"))
    # read_.update_value("app_info","qq","com.tencent.mm")
    # print(read_.getvalue("app_info","qq"))

