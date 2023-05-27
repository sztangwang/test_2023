import random

weights = {
    'UVC': {
        'open_uvc_and_live': 0.5,
        'open_uvc': 0.2,
        'close_uvc': 0.1,
        'uvc_live': 0.2
    },
    'HDMI': {
        'open_hdmi_and_live': 0.5,
        'open_hdmi': 0.2,
        'close_hdmi': 0.1,
        'hdmi_live': 0.2
    },
    'RTMP': {
        'open_rtmp_and_live': 0.1,
        'open_rtmp': 0,
        'close_rtmp': 0.2,
        'rtmp_live': 0.7
    }
}
class BasePageObject:
    def __init__(self, weights):
        self.weights = weights
        self.action_hits = {action: 0 for action in weights.keys()}

    def select_action(self):
        weights = self.weights
        if sum(weights.values()) != 1:
            raise ValueError("权重的和必须是1")
        choices = list(weights.keys())
        probs = list(weights.values())
        chosen_action = random.choices(choices, probs)[0]
        # 统计每个操作行为被选中的次数
        if chosen_action in self.action_hits:
            self.action_hits[chosen_action] += 1
        else:
            self.action_hits[chosen_action] = 1
        return getattr(self, chosen_action)



    def get_action_statistics(self):
        total_trials = sum(self.action_hits.values())
        action_statistics = {}
        for action, num_hits in self.action_hits.items():
            action_statistics[action] = round(num_hits / total_trials * 100, 2)
        return action_statistics




class SceneSelector:
    def __init__(self, factors):
        self.factors = factors

    def select(self):
        # 获取所有场景名称
        scenes = list(self.factors.keys())
        # 获取所有场景的权重
        weights = list(self.factors.values())
        # 根据权重随机选择一个场景
        chosen_scene = random.choices(scenes, weights)[0]
        return chosen_scene



    def run_trials(self, num_trials, page_objects):
        # 初始化一个字典，用于统计每个场景被选中的次数
        results = {scene: 0 for scene in self.factors.keys()}
        page_probabilities = {}
        for i in range(num_trials):
            chosen_scene = self.select()
            if chosen_scene not in page_objects:
                print(f"出错了，没有找到相应的场景，请检查配置!: {chosen_scene}")
                continue
            scene_page_object = page_objects[chosen_scene]
            action = scene_page_object.select_action()
            action()
            results[chosen_scene] += 1
            # 获取page的操作行为的概率字典，并将其合并到action_probabilities字典中
            page_probabilities[chosen_scene] = scene_page_object.get_action_statistics()
        total_trials = sum(results.values())
        for scene, num_hits in results.items():
            # 计算每个场景被选中的概率 ，四舍五入并且给概率加上%
            results[scene] = round(num_hits / total_trials * 100, 2)
            # 统计每个page的操作行为的概率
        return results,page_probabilities




class UvcPage(BasePageObject):
    def __init__(self, weights):
        super().__init__(weights)

    def open_uvc(self):
        print("open uvc")

    def close_uvc(self):
        print("close uvc")

    def uvc_live(self):
        print("live")
    def open_uvc_and_live(self):
        self.open_uvc()
        self.uvc_live()



class HDMIPage(BasePageObject):
    def __init__(self, weights):
        super().__init__(weights)
    def open_hdmi(self):
        print("open hdmi")
    def close_hdmi(self):
        print("close hdmi")
    def hdmi_live(self):
        print("live")
    def open_hdmi_and_live(self):
        self.open_hdmi()
        self.hdmi_live()

class RTMPPage(BasePageObject):
    def __init__(self, weights):
        super().__init__(weights)
    def open_rtmp(self):
        print("open rtmp")
    def close_rtmp(self):
        print("close rtmp")
    def rtmp_live(self):
        print("live")
    def open_rtmp_and_live(self):
        self.open_rtmp()
        self.rtmp_live()


if __name__ == '__main__':
    factors = {
        'UVC': 0.7,
        'HDMI': 0.0,
        'RTMP': 0.3
    }
    page_objects = {
        'UVC': UvcPage(weights['UVC']),
        'HDMI': HDMIPage(weights['HDMI']),
        'RTMP': RTMPPage(weights['RTMP'])
    }

    selector = SceneSelector(factors)
    num_trials = 1000
    results,page_result= selector.run_trials(num_trials, page_objects)
    print("场景执行概率：{} +\n ".format(results)," 每个场景下每个操作行为的概率：{}".format(page_result))