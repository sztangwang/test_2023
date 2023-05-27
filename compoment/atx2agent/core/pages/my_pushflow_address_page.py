from compoment.atx2agent.core.core_test.constant import BASE_DATA_PATH
from compoment.atx2agent.core.core_test.page_base import PageObject
from compoment.atx2agent.core.common.logs.log_uru import Logger
from compoment.atx2agent.core.pages.pushflow_address_page import PushflowAddressPage

logger = Logger().get_logger

class MyPushflowAddressPage(PageObject):
    def __init__(self, driver=None, device=None, path=f"{BASE_DATA_PATH}/home.yaml", file_name=f'my_pushflow_address_page'):
        super(MyPushflowAddressPage, self).__init__(driver, device, path, file_name)
        self.driver = driver
        self.device = device

    def goto_pushflow_address_page(self):
        """
        进入推流地址界面
        @return:
        """
        self.click(self.add_addr_btn)
        return PushflowAddressPage(self.driver, self.device)