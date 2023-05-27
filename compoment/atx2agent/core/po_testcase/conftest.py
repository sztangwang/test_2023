import allure
import pytest
from adbutils import adb
from compoment.atx2agent.core.common.logs.log_uru import Logger
from compoment.atx2agent.core.core_test.page_base import create_driver
from compoment.atx2agent.core.pages.launcher_home_page import CameraLauncherHomePage
from compoment.atx2agent.core.tools.driver_utils import kill_atx_agent
logger = Logger().get_logger


@pytest.fixture(scope='session')
def home(start_driver):
    driver,device=start_driver
    home = CameraLauncherHomePage(driver=driver,device=device,file_name="launcher_home")
    with allure.step(f"初始化 launcher ."):
        home.goto_launcher()
    yield home

@pytest.fixture(scope="session")
def get_cmd(request):
    """
    获取命令行参数
    """
    serial = request.config.getoption("--device")
    logger.info("serial: {}".format(serial))
    return serial


@pytest.fixture(scope="session")
def start_driver(request, get_cmd):
    """
    # 创建设备对象并连接一个设备
    :param device_id:
    :param app_id:
    :return:
    """
    # 1.连接设备，创建连接对象 uiautomator2
    logger.info("进行setup操作！！！")
    serial = get_cmd
    logger.info(f"serial: {serial}")
    driver = create_driver(serial)
    device = adb.device(serial)
    logger.info("driver_info:{}".format(driver))

    def driver_teardown():
        logger.info("自动化测试结束!")
        kill_atx_agent(driver, device)
    # 这样能保证 当初始化失败的时候，也能执行teardown操作
    request.addfinalizer(driver_teardown)
    return driver, device