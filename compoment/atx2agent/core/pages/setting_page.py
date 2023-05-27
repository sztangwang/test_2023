import time
from compoment.atx2agent.core.core_test.constant import BASE_DATA_PATH
from compoment.atx2agent.core.core_test.page_base import PageObject
from compoment.atx2agent.core.pages.about_camera_page import AboutCameraPage
from compoment.atx2agent.core.common.logs.log_uru import Logger
from compoment.atx2agent.core.pages.btpage import BtPage

logger = Logger().get_logger

class SettingPage(PageObject):
    def __init__(self, driver, device, path=f"{BASE_DATA_PATH}/home.yaml", file_name=f'setting_page'):
        super(SettingPage, self).__init__(driver, device, path, file_name)
        self.driver = driver
        self.device = device


    def goto_launcher(self):
        """返回launcher页面"""
        self.device.shell("input swipe 200 0 670 700")
        self.click(self.live_btn)

    # 进入关于相机页面
    def goto_about_the_camera_page(self):
        time.sleep(1)
        self.click(self.about_camera)
        return AboutCameraPage(self.driver, self.device)

    # 进入蓝牙界面
    def goto_bt_page(self):
        time.sleep(1)
        self.click(self.bluetooth)
        return BtPage(self.driver,self.device)
