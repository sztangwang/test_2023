import json
import yaml
from compoment.atx2agent.core.models.model import ProjectD
from compoment.atx2agent.core.tools.yaml_util import read_test_yaml

FeatureData = "FeatureData"
PerformanceData = "PerformanceData"
SuitConfigData = "SuitConfigData"
recordData = "recordData"
uvc_clientData = "uvc_clientData"
Repeat_FrameData = "Repeat_FrameData"
Exception_FrameData = "Exception_FrameData"


class SuiteConfigData:
    # 用例导入
    def __init__(self):
        self.suiteCase = {}
    def __str__(self):
        return "suiteCase: %s" % self.suiteCase
    # 从yaml 文件中读取用例导入数据
    def readSuiteConfigData(self, filePath):
        if filePath:
            with open(filePath, mode='r', encoding='utf-8') as f:
                try:
                    cases = yaml.load(stream=f, Loader=yaml.FullLoader)
                    cases_json = json.dumps(cases, ensure_ascii=False)
                    cases_obj = ProjectD.from_json(cases_json)
                   # print("cases_obj: %s" % cases_obj)
                    return cases_obj
                except Exception as e:
                    raise Exception("关键字用例格式错误，请检查格式.")

        else:
            print("case_path is None")
            raise Exception("case_path is None")



if __name__ == '__main__':
    suiteConfigData = SuiteConfigData()
    suiteConfigData.readSuiteConfigData(r"D:/python-workspace/Windows_Agent/compoment/atx2agent/core/testcases/case_demo.yaml")
