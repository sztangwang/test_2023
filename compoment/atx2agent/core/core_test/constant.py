
import os
from typing import Union


def get_env(name, base: Union[str, int] = ''):
    """
    从环境变量中获取指定的信息
    @param name: 环境变量信息
    @param base: 默认信息
    @return:
    """
    return os.getenv(name) and os.getenv(name).strip() or base


BASE_PATH = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
BASE_DATA_PATH = os.path.join(BASE_PATH, 'core','data')
SRC_PATH = os.path.join(BASE_PATH, 'src')
TOOL_PATH = os.path.join(SRC_PATH, 'tools')
ALLURE_TOOL_PATH = os.path.join(TOOL_PATH, 'allure-2.14.0/bin')

LOG_PATH = os.path.join(BASE_PATH, 'log')
REPORT_PATH = os.path.join(BASE_PATH, 'report')
TEST_PIC = os.path.join(REPORT_PATH, 'test_pic')
PERF_PATH = os.path.join(REPORT_PATH, 'perf')

for i in [LOG_PATH, REPORT_PATH, TEST_PIC, PERF_PATH]:
    if not os.path.exists(i):
        os.mkdir(i)

CASES = get_env("cases")  # 测试用例
HEADLESS = get_env("headless", "false")  # 是否不显示浏览器
CONCURRENT = get_env("concurrent", "否")  # 并发数 [0, 1, 2, 3, 4, auto, 否]
EMAIL = get_env("email")  # 邮件
ROBOT = get_env("robot")  # 企业微信群机器人
ProjectName = get_env("JOB_NAME", "非jenkins运行")  # 构建项目名称
BUILD_URL = get_env("BUILD_URL", "非jenkins运行")  # 构建项目URL
BUILD_NUMBER = get_env("BUILD_NUMBER", 0)  # 构建编号
APK_PATH = get_env("apk_path")  # 安装包地址
REMOTE_PORT = get_env("remote_port", "4723")  # 远程端口
REMOTE_URL = get_env("remote_url", "http://127.0.0.1")  # 远程地址
UDID = get_env("device", "1709c849")  # 手机udid
