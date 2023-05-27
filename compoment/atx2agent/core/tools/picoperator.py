import types
from copy import deepcopy
import cv2


# 图片比对算法
from airtest.aircv.keypoint_matching import KAZEMatching, BRISKMatching, AKAZEMatching, ORBMatching
from airtest.aircv.keypoint_matching_contrib import SIFTMatching, SURFMatching, BRIEFMatching
from airtest.aircv.multiscale_template_matching import MultiScaleTemplateMatchingPre, MultiScaleTemplateMatching
from airtest.aircv.template_matching import TemplateMatching

from compoment.atx2agent.core.common.logs.log_uru import Logger
from compoment.atx2agent.core.tools.cvtools import cocos_min_strategy, imread, get_resolution, crop_image
from compoment.atx2agent.core.tools.error import InvalidMatchingMethodError

logger = Logger().get_logger

MATCHING_METHODS = {
    "tpl": TemplateMatching,
    "mstpl": MultiScaleTemplateMatchingPre,
    "gmstpl": MultiScaleTemplateMatching,
    "kaze": KAZEMatching,
    "brisk": BRISKMatching,
    "akaze": AKAZEMatching,
    "orb": ORBMatching,
    "sift": SIFTMatching,
    "surf": SURFMatching,
    "brief": BRIEFMatching,
}


class TargetPos(object):
    """
    获取目标图片的不同位置，默认为中心点0
    1 2 3
    4 0 6
    7 8 9
    """
    LEFTUP, UP, RIGHTUP = 1, 2, 3
    LEFT, MID, RIGHT = 4, 5, 6
    LEFTDOWN, DOWN, RIGHTDOWN = 7, 8, 9

    def getXY(self, cvret, pos):
        if pos == 0 or pos == self.MID:
            return cvret["result"]
        rect = cvret.get("rectangle")
        if not rect:
            return cvret["result"]
        w = rect[2][0] - rect[0][0]
        h = rect[2][1] - rect[0][1]
        if pos == self.LEFTUP:
            return rect[0]
        elif pos == self.LEFTDOWN:
            return rect[1]
        elif pos == self.RIGHTDOWN:
            return rect[2]
        elif pos == self.RIGHTUP:
            return rect[3]
        elif pos == self.LEFT:
            return rect[0][0], rect[0][1] + h / 2
        elif pos == self.UP:
            return rect[0][0] + w / 2, rect[0][1]
        elif pos == self.RIGHT:
            return rect[2][0], rect[2][1] - h / 2
        elif pos == self.DOWN:
            return rect[2][0] - w / 2, rect[2][1]
        else:
            return cvret["result"]


class Template(object):

    def __init__(self, filename, threshold=None, target_pos=TargetPos.MID, record_pos=None, resolution=(), rgb=False,
                 scale_max=800, scale_step=0.005):
        """
        picture as touch/swipe/wait/exists target and extra info for cv match
        filename: 图片文件位置
        threshold: 门槛
        target_pos: 点击位置
        record_pos: 录制时的相对坐标
        resolution: 录制时的手机分辨率
        rgb: 识别结果是否使用rgb三通道进行校验.
        scale_max: 多尺度模板匹配最大范围.
        scale_step: 多尺度模板匹配搜索步长.
        """
        self.filename = filename
        self._filepath = None
        self.threshold = threshold or 0.7  # 门槛
        self.target_pos = target_pos  # 点击位置
        self.record_pos = record_pos
        self.resolution = resolution
        self.rgb = rgb
        self.scale_max = scale_max
        self.scale_step = scale_step

    @property
    def filepath(self):
        """
        获取图片全路径
        @return:
        """
        if self._filepath:
            return self._filepath
        return self.filename

    def __repr__(self):
        filepath = self.filepath
        return f"Template({filepath})"

    def match_in(self, screen):
        """

        @param screen: 当前页面截图
        @return:
        """
        match_result = self._cv_match(screen)
        logger.debug(f"match result: {match_result}")
        if not match_result:
            return None
        focus_pos = TargetPos().getXY(match_result, self.target_pos)
        return focus_pos

    def match_all_in(self, screen):
        image = self._imread()
        image = self._resize_image(image, screen, staticmethod(cocos_min_strategy))
        return self._find_all_template(image, screen)

    def _cv_match(self, screen):
        # in case image file not exist in current directory:
        ori_image = self._imread()
        # ori_image 目标图片
        # screen 当前页面截图
        image = self._resize_image(ori_image, screen,
                                   staticmethod(cocos_min_strategy))  # 根据 当时截取目标图片截图手机的分辨率 和 现在手机分辨率 来缩放 目标图片
        ret = None
        for method in ["mstpl", "tpl", "surf", "brisk"]:
            # get function definition and execute:
            func = MATCHING_METHODS.get(method, None)
            if func is None:
                raise InvalidMatchingMethodError(
                    f"Undefined method in CVSTRATEGY: '{method}', try 'kaze'/'brisk'/'akaze'/'orb'/'surf'/'sift'/'brief' instead.")
            else:
                try:
                    if method in ["mstpl", "gmstpl"]:
                        ret = self._try_match(func, ori_image, screen, threshold=self.threshold, rgb=self.rgb,
                                              record_pos=self.record_pos,
                                              resolution=self.resolution, scale_max=self.scale_max,
                                              scale_step=self.scale_step)
                    else:
                        ret = self._try_match(func, image, screen, threshold=self.threshold, rgb=self.rgb)
                except Exception as e:
                    logger.error(f"比对算法异常:{e}")
            if ret:
                break
        return ret

    @staticmethod
    def _try_match(func, *args, **kwargs):
        logger.debug(f"try match with {func.__name__}")
        try:
            ret = func(*args, **kwargs).find_best_result()
        except Exception as e:
            logger.error(e)
            return None
        else:
            return ret

    def _imread(self):
        return imread(self.filepath)

    def _find_all_template(self, image, screen):
        return TemplateMatching(image, screen, threshold=self.threshold, rgb=self.rgb).find_all_results()

    def _find_keypoint_result_in_predict_area(self, func, image, screen):
        if not self.record_pos:
            return None
        # calc predict area in screen
        image_wh, screen_resolution = get_resolution(image), get_resolution(screen)
        xmin, ymin, xmax, ymax = Predictor.get_predict_area(self.record_pos, image_wh, self.resolution,
                                                            screen_resolution)
        # crop predict image from screen
        predict_area = crop_image(screen, (xmin, ymin, xmax, ymax))
        if not predict_area.any():
            return None
        # keypoint matching in predicted area:
        ret_in_area = func(image, predict_area, threshold=self.threshold, rgb=self.rgb)
        # calc cv ret if found
        if not ret_in_area:
            return None
        ret = deepcopy(ret_in_area)
        if "rectangle" in ret:
            for idx, item in enumerate(ret["rectangle"]):
                ret["rectangle"][idx] = (item[0] + xmin, item[1] + ymin)
        ret["result"] = (ret_in_area["result"][0] + xmin, ret_in_area["result"][1] + ymin)
        return ret

    def _resize_image(self, image, screen, resize_method):
        """模板匹配中，将输入的截图适配成 等待模板匹配的截图."""
        # 未记录录制分辨率，跳过
        if not self.resolution:
            return image
        screen_resolution = get_resolution(screen)
        # 如果分辨率一致，则不需要进行im_search的适配:
        #   * 手机分辨率 和 截图的分辨率一致
        if tuple(self.resolution) == tuple(screen_resolution) or resize_method is None:
            return image
        if isinstance(resize_method, types.MethodType):
            resize_method = resize_method.__func__
        # 分辨率不一致则进行适配，默认使用cocos_min_strategy:
        h, w = image.shape[:2]
        w_re, h_re = resize_method(w, h, self.resolution, screen_resolution)
        # 确保w_re和h_re > 0, 至少有1个像素:
        w_re, h_re = max(1, w_re), max(1, h_re)
        # 调试代码: 输出调试信息.
        logger.debug(f"resize: ({w}, {h})->({w_re}, {h_re}), resolution: {self.resolution}=>{screen_resolution}")
        # 进行图片缩放:
        image = cv2.resize(image, (w_re, h_re))
        return image


class Predictor(object):
    """
    this class predicts the press_point and the area to search im_search.
    """

    DEVIATION = 100

    @staticmethod
    def count_record_pos(pos, resolution):
        """计算坐标对应的中点偏移值相对于分辨率的百分比."""
        _w, _h = resolution
        # 都按宽度缩放，针对G18的实验结论
        delta_x = (pos[0] - _w * 0.5) / _w
        delta_y = (pos[1] - _h * 0.5) / _w
        delta_x = round(delta_x, 3)
        delta_y = round(delta_y, 3)
        return delta_x, delta_y

    @classmethod
    def get_predict_point(cls, record_pos, screen_resolution):
        """预测缩放后的点击位置点."""
        delta_x, delta_y = record_pos
        _w, _h = screen_resolution
        target_x = delta_x * _w + _w * 0.5
        target_y = delta_y * _w + _h * 0.5
        return target_x, target_y

    @classmethod
    def get_predict_area(cls, record_pos, image_wh, image_resolution=(), screen_resolution=()):
        """Get predicted area in screen."""
        x, y = cls.get_predict_point(record_pos, screen_resolution)
        # The prediction area should depend on the image size:
        if image_resolution:
            predict_x_radius = int(image_wh[0] * screen_resolution[0] / (2 * image_resolution[0])) + cls.DEVIATION
            predict_y_radius = int(image_wh[1] * screen_resolution[1] / (2 * image_resolution[1])) + cls.DEVIATION
        else:
            predict_x_radius, predict_y_radius = int(image_wh[0] / 2) + cls.DEVIATION, int(
                image_wh[1] / 2) + cls.DEVIATION
        area = (x - predict_x_radius, y - predict_y_radius, x + predict_x_radius, y + predict_y_radius)
        return area
