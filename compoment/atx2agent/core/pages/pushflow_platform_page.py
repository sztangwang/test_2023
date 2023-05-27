from compoment.atx2agent.core.core_test.constant import BASE_DATA_PATH
from compoment.atx2agent.core.core_test.page_base import PageObject
from compoment.atx2agent.core.common.logs.log_uru import Logger

logger = Logger().get_logger

class PushflowPlatformPage(PageObject):

    def __init__(self, driver=None, device=None, path=f"{BASE_DATA_PATH}/home.yaml",
                 file_name=f'pushflow_platform_page'):
        super(PushflowPlatformPage, self).__init__(driver, device, path, file_name)
        self.driver = driver
        self.device = device