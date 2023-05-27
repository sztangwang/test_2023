from compoment.atx2agent.core.core_test.constant import BASE_DATA_PATH
from compoment.atx2agent.core.core_test.page_base import PageObject
from compoment.atx2agent.core.common.logs.log_uru import Logger
logger = Logger().get_logger



class BtPage(PageObject):
    def __init__(self, driver, device, path=f"{BASE_DATA_PATH}/home.yaml", file_name=f'bt_page'):
        super(BtPage, self).__init__(driver, device, path, file_name)
        self.driver = driver
        self.device = device

    def goto_launcher(self):
        """返回launcher页面"""
        self.device.shell("input swipe 200 0 670 700")
       # self.click(live_btn)

    # 进入蓝牙设置
    def goto_bluetooth_setting(self):
        self.get_locator(self.bt_switch)
        self.assert_exited(self.bt_switch)
        self.assert_exited(self.device_name)
        if self.get_info(self.bt_switch)['text'] == '关闭':
            self.click(self.bt_switch)
            if self.find_element_exists(self.bt_device, timeout=5):
                self.assert_exited(self.bt_device)
            else:
                logger.info("周围没有蓝牙设备！")
        self.goto_launcher()
