import pytest
import time
import os
from adbutils import adb

from compoment.atx2agent.core.core_test import device_facade
from compoment.atx2agent.core.core_test.device_facade import DeviceFacade
from compoment.atx2agent.core.core_test.page_base import create_driver
from compoment.atx2agent.core.tools import driver_utils
from compoment.atx2agent.core.tools.driver_utils import kill_atx_agent
from compoment.atx2agent.core.common.logs.log_uru import Logger
from compoment.atx2agent.core.config.config import ReadConfig, YamlConfig
logger = Logger().get_logger


class Project:
    dir = os.path.abspath(os.path.dirname(__file__))
    test_data_dir = os.path.dirname(__file__)


def pytest_addoption(parser):
    """
    添加命令行参数
    parser.addoption为固定写法
    default 设置一个默认值，此处设置默认值为test
    choices 参数范围，传入其他值无效
    help 帮助信息
    """
    parser.addoption("--env", default="core_test", choices=["dev", "core_test", "pre"], help="enviroment parameter")
    parser.addoption("--cmdopt", action="store", default="type1", help="my option: type1 or type2")
    parser.addoption("--sn", action="store", help="test device sn")
    parser.addoption("--cases",action="append",default=[],help="cases")
    parser.addoption("--device", action="store", help="test device sn")




@pytest.fixture(scope="session")
def get_env(request):
    """
    获取命令行参数
    :param request:
    :return:
    """
    env = request.config.getoption("--env")
    cmdopt = request.config.getoption("--cmdopt")
    logger.info(f"env: {env}")
    logger.info(f"cmdopt: {cmdopt}")
    return env,cmdopt

@pytest.fixture(scope="session")
def get_cases(request):
    """
    获取用例列表
    @param request:
    @return:
    """
    cases = request.config.getoption("--cases")
    return cases



@pytest.fixture(scope="session")
def get_cmd_device(request):
    """
    获取命令行参数
    """
    env = request.config.getoption("--env")
    # 获取命令行参数
    device_facade.SN = request.config.getoption("--sn")
    logger.info(f"设备SN: {device_facade.SN}")
    serial = request.config.getoption("--cmdopt")
    logger.info("serial: {}".format(serial))
    device_facade.ENV = env
    logger.info(f"环境: {env}")

    return device_facade.ENV,serial


@pytest.fixture(scope="session")
def start_device(request, get_cmd_device):
    """
    # 创建设备对象并连接一个设备
    :param device_id:
    :param app_id:
    :return:
    """
   # global device
    # 1.连接设备，创建连接对象 uiautomator2
    logger.info("进行setup操作！！！")
    env, serial = get_cmd_device
    logger.info(f"环境: {env}")
    logger.info(f"serial: {serial}")
    driver = DeviceFacade(serial)
    device = adb.device(serial)
    logger.info("driver_info:::",driver)
    driver.get_device_info(driver)

    def driver_teardown():
        logger.info("自动化测试结束!{}{}".format(driver,device))
        kill_atx_agent(driver, device)
    # 这样能保证 当初始化失败的时候，也能执行teardown操作
    request.addfinalizer(driver_teardown)
    return driver, device

def pytest_collection_modifyitems(items):
    """
    测试用例收集完成时, 将收集到的item的name和nodeid的中文显示在控制台上
    :return:
    """
    for item in items:
        item.name = item.name.encode("utf-8").decode("unicode_escape")
        item._nodeid = item.nodeid.encode("utf-8").decode("unicode_escape")


 # 定义单个标签
def pytest_configure(config):
    config.addinivalue_line(
        "markers", "smoke"
    )

def pytest_terminal_summary(terminalreporter):
    """
    收集测试结果
    """
    _PASSED = len([i for i in terminalreporter.stats.get('passed', []) if i.when != 'teardown'])
    _ERROR = len([i for i in terminalreporter.stats.get('error', []) if i.when != 'teardown'])
    _FAILED = len([i for i in terminalreporter.stats.get('failed', []) if i.when != 'teardown'])
    _SKIPPED = len([i for i in terminalreporter.stats.get('skipped', []) if i.when != 'teardown'])
    _TOTAL = terminalreporter._numcollected
    _TIMES = time.time() - terminalreporter._sessionstarttime
    logger.info(f"成功用例数: {_PASSED}")
    logger.error(f"异常用例数: {_ERROR}")
    logger.error(f"失败用例数: {_FAILED}")
    logger.warning(f"跳过用例数: {_SKIPPED}")
    logger.info("用例执行时长: %.2f" % _TIMES + " s")
    try:
        _RATE = round((_PASSED + _SKIPPED) / _TOTAL * 100, 2)
        logger.info("用例成功率: %.2f" % _RATE + " %")
    except ZeroDivisionError:
        logger.info("用例成功率: 0.00 %")



def pytest_sessionfinish(session,exitstatus):
    passed_tests =[]
    failed_tests =[]
    for test in session.testscollected:
        if test.nodeid not in session.config.cache.get("cache/failed_tests",[]):
            passed_tests.append(test)
        else:
            failed_tests.append(test)
    session.config.passed_tests = passed_tests
    session.config.failed_tests = failed_tests


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """
    钩子函数：获取每个用例的状态
    将失败的用例截图，并保存到allure报告中
    """
    # 获取钩子方法的调用结果
    my_results = yield
    rep = my_results.get_result()
    # 获取用例call，执行结果是失败的，不包含 setup/teardown

    logger.info("测试报告：{}".format(rep))
    logger.info("测试步骤：{}".format(rep.when))
    logger.info("测试结果：{}".format(rep.outcome))
    logger.info("测试节点：{}".format(rep.nodeid))


    if rep.when == "call" and rep.failed:
        mode = "a" if os.path.exists("failures") else "w"
        with open("failures", mode) as f:
            # let's also access a fixtures for the fun of it
            if "tmpdir" in item.fixturenames:
                extra = " (%s)" % item.funcargs["tmpdir"]
            else:
                extra = ""
            f.write(rep.nodeid + extra + "\n")
        # 添加allure报告截图
        # if hasattr(self.driver, "get_screenshot_as_png"):
        #     with allure.step("添加失败截图"):
        #         allure.attach(driver.get_screenshot_as_png(), "失败截图", allure.attachment_type.PNG)


@pytest.fixture(scope="session")
def config_yaml():
    config_path = os.path.join(Project.dir, "compoment/atx2agent/conf.yaml")
    yaml = YamlConfig(config_path)
    return yaml


@pytest.fixture(scope="session")
def config_ini():
    config_path = os.path.join(Project.dir, "conf.ini")
    ini = ReadConfig(config_path)
    return ini








