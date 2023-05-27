from compoment.atx2agent.core.core_test.constant import BASE_DATA_PATH
from compoment.atx2agent.core.core_test.page_base import PageObject
from compoment.atx2agent.core.common.logs.log_uru import Logger
from compoment.atx2agent.core.pages.pushflow_platform_page import PushflowPlatformPage
from compoment.atx2agent.core.tools.data_util import generate_name
logger = Logger().get_logger

class PushflowAddressPage(PageObject):
    def __init__(self, driver=None, device=None, path=f"{BASE_DATA_PATH}/home.yaml", file_name=f'pushflow_address_page'):
        super(PushflowAddressPage, self).__init__(driver, device, path, file_name)
        self.driver = driver
        self.device = device
        self.add_name=generate_name()


    def add_address(self):
        """
        添加推流地址
        @return:
        """
        address = 'rtmp://192.168.69.100:1935/stream/'
        push_key = 'FF123456FF'
        # 点击手动添加地址
        self.click(self.handler_add_address_btn)
        # 输入推流地址名称
        self.input(self.address_name, self.add_name)
        self.device.shell("input tap 300 100")
       # self.swip_down()
        # 输入推流地址
        self.input(self.pushflow_address_input, address)
        self.device.shell("input tap 300 100")
       # self.swip_down()
        # 输入推流秘钥
        self.input(self.pushflow_address_key, push_key)
        self.device.shell("input tap 300 100")
        # self.swip_down()
        # 点击完成设置
        self.click(self.complete_btn)
        self.enter_pushflow_platform_page()
        # 校验新增的推流地址名称存在
       #  self.assert_exited(self.get_text(self.push_item_name))
       # todo 这个断言有问题，不应该在这个界面断言，应该在推流平台界面断言

    def enter_pushflow_platform_page(self):
        """
        进入推流平台页面
        @return:
        """
        logger.info(self.get_info(self.push_all_btn)['text'])
        if self.get_info(self.push_all_btn)['text'] != '全部':
            self.click(self.push_all_btn)
        else:
            self.add_address()
        return PushflowPlatformPage(self.driver, self.device)


