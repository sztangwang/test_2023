import allure
from compoment.atx2agent.core.common.logs.log_uru import Logger
logger = Logger().get_logger



class TestBtCase:
    """
     蓝牙功能测试类
    """
    @allure.story("测试进入蓝牙设置页")
    def test_goto_bluetooth_setting(self, home):
        home.open_quick_setting().open_setting().goto_bt_page().goto_bluetooth_setting()


