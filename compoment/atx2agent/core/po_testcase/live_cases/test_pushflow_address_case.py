import allure
import pytest


@allure.story("推流地址用例测试")
class TestPushflowAddressCase:
    @allure.story("进入推流地址页，新增推流地址")
    @pytest.mark.repeat(1)
    def test_add_address(self, home):
        home.goto_my_pushflow_address_page().goto_pushflow_address_page().add_address()