import random
import re
import string


class BuiltinFunctions:
    """
    内置函数类
    """
    @staticmethod
    def random_name():
        return ''.join(random.sample(string.ascii_letters + string.digits, 6))

    @staticmethod
    def random_phone():
        return ''.join(random.sample(string.digits, 11))

    @staticmethod
    def random_int(start, end):
        r_int =random.randint(int(start), int(end))
        return r_int


def get_value(value):
    """
    获取内置函数的值 ,如果不是以${{}}开头的,则直接返回
    :param value ${{value}}
    """
    # 分三种格式 1.${{}},2.${} ,3.原样返回
    if value.startswith('${{') and value.endswith('}}'):
        # 去掉前后缀
        value = value[3:-2]
        # 分割函数名和多个参数
        func_name, *args = value.split(':')
        # 获取函数
        func = getattr(BuiltinFunctions, func_name)
        # 执行函数
        return func(*args)
    elif value.startswith('${') and value.endswith('}'):
        # todo 如果 value 是 ${} ,则从全局变量中获取变量的值
       return value[2:-1]
    else:
        return value


def parse_value(key, global_var):
    # 匹配所有的 ${}
    pattern = re.compile(r'\${([^}]+)}')
    if isinstance(key, float) or isinstance(key, int):
         return key
    while True:
        match = pattern.search(key)
        if not match:
            break
        var_name = match.group(1)
        # 从全局变量中获取变量的值
        var_value = get_value(global_var.get(var_name))
        if var_value is None:
            raise ValueError("var_name: {} is not found".format(var_name))
        key = key.replace(match.group(), str(var_value))
       # key = key[:match.start()] + var_value + key[match.end():]
    return key

if __name__ == '__main__':
    value = '${r_name}'
    global_val = {'r_name': '${{random_name}}'}
    print(parse_value(value,global_val))
    #
    # value1 = '${url}'
    # global_val1 = {'url': 'rtmp://192.168.42.18:1935/stream/pc_test1'}
    # print(parse_value(value1,global_val1))
    #
    # value2= '${time}'
    # global_val2 = {'time': '2020-12-12 12:12:12'}
    # print(parse_value(value2,global_val2))
    #
    # value3 ='${c_name}'
    # global_val3 = {'c_name': '中文名字'}
    # print(parse_value(value3,global_val3))
    #
    # value4 = '${r_int}'
    # global_val4 = {'r_int': '${{random_int:1:100}}'}
    # print(parse_value(value4,global_val4))
    #
    # value5 = '${r_phone}'
    # global_val5 = {'r_phone': '${r_int}'}
    # print(parse_value(value5,global_val5))

    value6= 'com.hollyland.cameralive'
    global_val6 = {'r_phone': '${{random_phone}}'}
    print(parse_value(value6,global_val6))

    value7 = 'com.hollyland.cameralive'
    global_val7 = {'push_url_name': '${{random_name}}', 'push_url': 'rtmp://192.168.42.18:1935/stream/pc_test1', 'timeout': '3'}
    print(parse_value(value7,global_val7))


    value8 ='3.0'
    global_val8 = {'push_url_name': '${{random_name}}', 'push_url': 'rtmp://192.168.42.18:1935/stream/pc_test1', 'timeout': '3'}
    print(parse_value(value8,global_val8))