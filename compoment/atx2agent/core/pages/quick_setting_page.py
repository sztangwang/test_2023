from compoment.atx2agent.core.core_test.constant import BASE_DATA_PATH
from compoment.atx2agent.core.core_test.page_base import PageObject
from compoment.atx2agent.core.pages.setting_page import SettingPage
from compoment.atx2agent.core.common.logs.log_uru import Logger
logger = Logger().get_logger


class QuickSettingPage(PageObject):
    def __init__(self, driver=None, device=None, path=f"{BASE_DATA_PATH}\\home.yaml", file_name=f'quick_setting_page'):
        super(QuickSettingPage, self).__init__(driver, device, path, file_name)
        self.driver = driver
        self.device = device


    # 打开设置界面
    def open_setting(self):
        # 下拉屏幕
        self.click(self.setting_btn)
        self.assert_exited(self.wired_network)
        self.assert_exited(self.about_camera)
        return SettingPage(self.driver, self.device)

    def goto_launcher(self):
        """返回launcher页面"""
        self.device.shell("input swipe 200 0 670 700")
        print("locator_t:",self.live_btn)
        self.click(self.live_btn)

if __name__ == '__main__':
    quick_setting_page = QuickSettingPage()
    quick_setting_page.goto_launcher()
    print(quick_setting_page.live_btn)