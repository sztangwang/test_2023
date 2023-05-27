import json
import os

from compoment.atx2agent.core.config.config import YamlConfig
from compoment.atx2agent.core.core_test.test_android import GlobalVar
from compoment.atx2agent.core.models.model import ProjectD, Case
from compoment.atx2agent.core.tools.yaml_util import read_test_yaml
from conftest import Project


class ParseCase:
    """
     解析yaml 测试用例为对象
    """
    def __init__(self):
        self.globalVar = GlobalVar()
        self.yaml = self.config_yaml()

    def config_yaml(self):
        config_path = os.path.join(Project.dir, "compoment","atx2agent" "\\conf.yaml")
        yaml = YamlConfig(config_path)
        return yaml

    def get_project_dto(self):
        config_yaml = self.yaml
        cases_path = config_yaml.get_node_key_value("env.test.run_info", "case_path")
        case_file = config_yaml.get_node_key_value("env.test.run_info", "case_file")
        case_path = os.path.join(cases_path+case_file)
        if case_path is None:
            raise Exception("case_path is None")
        else:
            cases = read_test_yaml(case_path)
            cases_json = json.dumps(cases, ensure_ascii=False)
            cases_obj = ProjectD.from_json(cases_json)
            return cases_obj

    def get_case_info_by_case_id(self,case_id,data):
        """
        根据case_id 返回case 对象
        @param case_id:
        @return:
        """
        if data is None:
            return None
            # 获取用例集
        case_json_list = []
        for _modules in data.project.modules:
            for _case in _modules.module.cases:
                if _case.case.caseId == int(case_id):
                    list_json = Case.to_json(_case.case)
                    # 如果列表中存在该用例，则不添加
                    if list_json not in case_json_list:
                        case_json_list.append(list_json)
        return case_json_list


if __name__ == '__main__':
    test_case =ParseCase()
    cases=test_case.get_project_dto()
    for _case in cases.cases:
        case = _case.case
        print(type(case))
        print(case.name)
        print(case.desc)
        print(case.globalVal,type(case.globalVal))
        globalval = case.globalVal
        for _globalval in globalval:
            print(_globalval.name)
            print(_globalval.value)
        presteps = case.presteps
        for _prestep in presteps:
           step = _prestep.step
           print(step.name)
           print(step.desc)
           print(step.action)
           print(step.params)
           locators = step.locators
           if locators is not None:
              # print("locators ---->>> "+locators)
               for _locator in locators:
                 print(_locator.name)
                 print(_locator.locatorType)
                 print(_locator.locatorValue)
                 print(_locator.locateDesc)
