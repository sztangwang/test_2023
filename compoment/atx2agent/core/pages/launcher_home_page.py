import time
import allure
from compoment.atx2agent.core.common.logs.log_uru import Logger
from compoment.atx2agent.core.core_test.constant import BASE_DATA_PATH
from compoment.atx2agent.core.core_test.page_base import PageObject
from compoment.atx2agent.core.pages.my_pushflow_address_page import MyPushflowAddressPage
from compoment.atx2agent.core.pages.quick_setting_page import QuickSettingPage
from compoment.atx2agent.core.tools.adb_utils import is_network

logger = Logger().get_logger

class CameraLauncherHomePage(PageObject):
    def __init__(self, driver=None, device=None, path=f"{BASE_DATA_PATH}/home.yaml", file_name=f'launcher_home'):
        super(CameraLauncherHomePage, self).__init__(driver,device,path, file_name)
        self.driver = driver
        self.device = device


    def goto_launcher(self):
        """返回launcher页面"""
        # 上滑回到launcher
        self.device.shell("input swipe 500 1910  770 1000")
        time.sleep(0.25)
        self.device.shell("input swipe 200 0 670 700")
        self.click(self.living_btn)
        self.device.shell("input tap 100 200")
        self.wait_element(self.beauty_btn)


    @allure.step("打开设置界面")
    def open_quick_setting(self):
        # 下拉屏幕
        self.device.shell("input swipe 200 0 670 700")
        self.assert_exited(self.bt_switch)
        self.assert_exited(self.auto_rotation)
        self.assert_exited(self.menu)
        self.assert_exited(self.setting)
        self.assert_exited(self.live)
        self.assert_exited(self.hdmi)
        self.assert_exited(self.uvc)
        self.assert_exited(self.volume)
        return QuickSettingPage(self.driver, self.device)

    # 测试首页默认为直播模式
    def launcher_default(self):
        # 先判断是否有推流地址，没有则新增
        self.click(self.beauty_btn)
        exist_addr = self.find_element_exists(self.addr_name, timeout=2)
        if exist_addr:
            logger.info("存在推流地址")
        else:
            logger.info("没有推流地址，请新增推流地址后测试！")
            return
        self.device.shell("input tap 180 300")
        # 判断是否有网络
        if is_network(self.device):
            # 开启直播
            self.click(self.click_btn)
            if self.find_element_exists(self.begin_live_text, timeout=5):
                if self.find_element_exists(self.quite_live):
                    self.wait_element(self.quite_live)
                    self.click(self.quite_live)
                    self.click(self.quite_live_ok_text)
                else:
                    self.find_element_exists(self.enter_live_fail_text, timeout=5)
                    self.click(self.enter_live_fail_text)
            else:
                logger.info("默认不是直播")
        self.find_element_exists(self.photo_btn, timeout=10)



    def goto_my_pushflow_address_page(self):
        """
        进入我的推流地址页面
        @return:
        """
        self.click(self.beauty_btn)
        return MyPushflowAddressPage(self.driver, self.device)

if __name__ == '__main__':
    home_h5 = CameraLauncherHomePage()
    print(type(home_h5))
    print(home_h5.registered)