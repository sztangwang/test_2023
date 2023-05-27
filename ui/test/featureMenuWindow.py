from ui.test.featureMenuLayout import FeatureMenuLayout


class FeatureMenuWindow(FeatureMenuLayout):

    def __init__(self, *args, **kwargs):
        super(FeatureMenuLayout, self).__init__(*args, **kwargs)
        self.initUI(self)

    def initData(self):
        self.initCaseData()
        self.initDeviceData()

    def selectCases(self):
        """
        查询用例状态
        """
        pass

    def initCaseData(self):
        """
        初始化用例数据
        """
        pass

    def initDeviceData(self):
        """
        初始化设备数据
        """
        pass

    def getUserChoiceCases(self):
        """
        获取用户当前选择的用例
        """
        pass

    def resetCaseState(self):
        """
        重置选项状态
        """
        pass

    def confirm(self):
        """
        确认选择
        """
        pass

    def refreshCases(self):
        """
        刷新用例
        """
        pass
