from enum import Enum
import pytest

from compoment.atx2agent.core.common.logs.log_uru import Logger
from compoment.atx2agent.core.core_test.device_facade import DeviceFacade
from compoment.atx2agent.core.core_test.functions import parse_value
from utils.fileutils import read_case_from_file, list_class_to_json, list_json_to_dict, dict_list_to_new_dict
import ui.test.globalvar as gl

logger = Logger().get_logger


# 定义步骤类型枚举
class StepType(Enum):
    # 正常步骤
    NORMAL_STEP = 'steps'
    # 前置步骤
    PRE_STEP = 'presteps'
    # 后置步骤
    POST_STEP = 'poststeps'

def get_case_list():
    """
    获取用例列表
    @return:
    """
    # 获取当前目录路径
    case_list= read_case_from_file()
    case_json = list_class_to_json(case_list)
    cases_dict = dict_list_to_new_dict(list_json_to_dict(case_json))
    return cases_dict



class GlobalVar:
    def __init__(self):
        self._global_dict = {}

    def set_value(self, key, value):
        self._global_dict[key] = value

    def get_value(self, key, defValue=None):
        try:
            return self._global_dict[key]
        except KeyError:
            return defValue

    @property
    def get_global_dict(self):
        return self._global_dict

    def clear(self):
        self._global_dict.clear()

    def __str__(self):
        return str(self._global_dict)


def run_test2(device,cases):
    logger.info("--cases={}".format(cases.get('cases')))
    pytest.main(['-vvsqk', 'test_function', '--alluredir=result', '--clean-alluredir',
                 '--cmdopt={}'.format(device.serial)])



def pytest_generate_tests(metafunc):
    # cases_dict = get_case_list()
    if 'case' in metafunc.fixturenames:
        # if cases_dict:
        #     cases =cases_dict.get("cases")
            cases_dict = gl.get_value("kw_cases")
            cases=cases_dict.get("cases")
            metafunc.parametrize('case', cases)

@pytest.fixture(scope="session")
def case():
     # cases_dict = get_case_list()
     # return cases_dict.get("cases")
     cases = gl.get_value("kw_cases")
     return cases.get('cases')


@pytest.mark.usefixtures("case")
def test_function(case,start_device):
    driver, device = start_device
    cases = Case(case, driver, device)
    # 获取全局变量的数据
    global_var_dict = cases.global_val_dict
    logger.info("全局变量的数据：{}".format(global_var_dict))
    logger.info("执行前置用例步骤")
    cases.run_cases(StepType.PRE_STEP)
    logger.info("执行用例步骤")
    cases.run_cases(StepType.NORMAL_STEP)
    logger.info("执行后置用例步骤")
    cases.run_cases(StepType.POST_STEP)






class Locator:
    def __init__(self, locator_data=None):
        self.locator_data = locator_data
        self.name = locator_data.get('name')
        self.desc = locator_data.get('locateDesc')
        self.type = locator_data.get('locatorType')
        self.value = locator_data.get('locatorValue')
        self.locator = dict()

    def __str__(self):
        return str(self.locator_data)


    @property
    def get_locator_dict(self):
        self.locator.update({self.type: self.value})
        return self.locator

class Step:
    def __init__(self,step):
        self.step = step.get("step")
        self.name = self.step.get('name')
        self.desc = self.step.get('desc')
        self.action = self.step.get('action')
        self.locators = self.step.get('locators')
        self.params = self.step.get('params')

    def __getattr__(self, item):
        if item in ['name', 'desc', 'action', 'locators', 'params']:
            return getattr(self, item)
        raise AttributeError

    def __str__(self):
        return str(self.step)

    def get_locator(self, locator):
        """获取元素"""
        if len(locator) < 0:
            raise ValueError('locator 不能为空')
        if isinstance(locator, list):
            if isinstance(locator, str):
                locator = self.locators.get(locator)
                return Locator(locator)
        else:
            raise AttributeError(f'页面对象 {self.__class__.__name__} 没有找到元素 {locator}')

    def run(self, driver: DeviceFacade, globalVar: GlobalVar=None):
        """
        执行步骤
        :param driver:
        :return:
        """
        locator_dict = dict()
        action_name = "k_" + self.action
        if hasattr(driver, action_name):
            method = getattr(driver, action_name)
            params= self.params
            # if len(params)>0:
            if params is not None:
                # 如果 params 的value 值是变量，则替换变量
                for key, value in params.items():
                    value =parse_value(value, globalVar.get_global_dict)  # 替换变量
                    params[key] = value
                if self.locators is None:
                    method(**params)
                    logger.info("执行步骤：{0}, 执行action：{1}, 执行参数：{2}".format(self.step,self.action,params))
                else:
                    for loc in self.locators:
                        locator = Locator(loc)
                        locator_dict.update(locator.get_locator_dict)
                    logger.info("执行步骤：{0}, 执行action：{1}, 执行locator：{2}, 执行参数：{3}".format(self.step,self.action,locator_dict,params))
                    method(locator_dict,**params)
            else:
                if self.locators is None:
                    method()
                    logger.info("执行步骤：{0}, 执行action：{1}".format(self.step,self.action))
                else:
                    for loc in self.locators:
                        locator = Locator(loc)
                        locator_dict.update(locator.get_locator_dict)
                    logger.info("执行步骤：{0}, 执行action：{1}, 执行locator：{2},".format(self.step,self.action,locator_dict))
                    method(locator_dict)


class Case:
    def __init__(self,case_data,driver,device):
        self.case_data = case_data
        self.driver = driver
        self.device = device
        self.globalVar = GlobalVar()
        if self.driver is None or self.device is None:
            raise ValueError("driver is None or device is None")
        if isinstance(self.case_data, dict):
            self.case = self.case_data.get('case')
            self.name = self.case.get('name')
            self.case_id = self.case.get("caseId")
            self.level= self.case.get("level")
            self.status=self.case.get("status")
            self.desc = self.case.get('desc')
            global_var = self.case.get('globalVal')
            self.global_val_dict = dict()
            if len(global_var) > 0:
                self.global_val_dict = {item.get('name'): item.get('value') for item in global_var}
                # 将全局变量的dict 保存到GlobalVar类中
                for key, value in self.global_val_dict.items():
                    self.globalVar.set_value(key, value)
                    logger.info("设置全局变量：{0}={1}".format(key, value))

    def run_cases(self,stepType:StepType):
        """
        根据步骤类型执行用例
        """
        # 获取步骤类型
        stepType = stepType.value
        # 获取步骤列表
        self._run(self.case,stepType)


    def _run(self,case,stepType):
        """
        执行用例
        """
        # 获取所有case 字典的key
        case_keys = case.keys()
        # 根据stepType 值的不同，获取对应的步骤列表
        if stepType in case_keys:
            steps = case.get(stepType)
            self._run_step(steps)
        else:
            raise AttributeError("用例中没有找到步骤类型：{}".format(stepType))


    def __getattr__(self, attr):
        if attr in ['name', 'desc', 'globalVar','global_val_dict']:
            return getattr(self, attr)
        raise AttributeError

    def __str__(self):
        return str(self.case_data)

    def _run_step(self,steps):
        for step in steps:
            step = Step(step)
            step.run(self.driver,self.globalVar)




if __name__ == '__main__':
    pass
