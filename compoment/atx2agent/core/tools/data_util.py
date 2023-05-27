import random
import string


def generate_name():
    """
    随机生成一个名字，4位
    @return:
    """
    name = ''.join(random.sample(string.ascii_letters + string.digits, 4))
    return name