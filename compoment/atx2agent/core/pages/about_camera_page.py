from compoment.atx2agent.core.common.logs.log_uru import Logger
from compoment.atx2agent.core.core_test.constant import BASE_DATA_PATH
from compoment.atx2agent.core.core_test.page_base import BasePage

logger = Logger().get_logger
class AboutCameraPage(BasePage):
    def __init__(self, driver, device, path=f"{BASE_DATA_PATH}/home.yaml", file_name=f'about_camera_page'):
        super(AboutCameraPage, self).__init__(driver, device, path, file_name)
        self.driver = driver
        self.device = device


    def enter_about_camera(self):
        self.assert_exited("设备名称")
        self.assert_exited("设备型号")
        self.assert_exited("运行内存")
        self.assert_exited("设备存储")
        self.assert_exited("内核版本")
        self.assert_exited("固件版本")
        self.assert_exited("状态信息")
        self.goto_launcher()
