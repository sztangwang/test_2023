from dataclasses import dataclass
from typing import List, Optional

from dataclasses_json import dataclass_json



@dataclass_json
@dataclass
class Case:
    name: str = ""
    desc: str = ""
    globalVal: List[dict] = None
    preSteps: List[dict] = None
    steps: List[dict] = None
    postSteps: List[dict] = None

    def __str__(self):
        return f"Case(name={self.name}, desc={self.desc}, globalVal={self.globalVal}, preSteps={self.preSteps}, steps={self.steps}, postSteps={self.postSteps})"

    def __repr__(self):
        return self.__str__()


# 定义一个测试用例执行类
@dataclass_json
@dataclass
class RunnerTest:
    # 测试模式类型
    testModel: str = ''
    # 测试用例
    testCaseList: str = ''
    # 测试设备
    device: str = ''
    # 测试时间
    time: str = ''
    # 测试引擎
    testEngine: str = ''
    # 测试结果
    result: str = ''

    def __str__(self):
        return "测试用例: %s, 测试设备: %s, 测试时间: %s, 测试模块: %s, 测试引擎: %s, 测试结果: %s" % (
            self.testCaseList, self.device, self.time, self.testModel, self.testEngine, self.result)


@dataclass_json
@dataclass
class RunnerDto:
    testType: any =None
    testCaseList: list[any] =None
    device_list: list[any] =None


if __name__ == '__main__':
    case = Case("test", "test")
    print(case)
    print(repr(case))
    print(str(case))
    runnerTest = RunnerTest()

    runnerTest.testCaseList = [case]
    print(type(runnerTest.testCaseList))
    print(runnerTest)
