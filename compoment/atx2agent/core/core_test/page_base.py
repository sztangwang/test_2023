import os
import re
import string
import time
from datetime import datetime
from enum import Enum, auto
from random import uniform, randint
from subprocess import run, PIPE
from time import sleep
from typing import Optional
import allure
import numpy as np
import uiautomator2
import yaml
from uiautomator2 import UiObject, Selector, UiObjectNotFoundError, ServerError
from uiautomator2.xpath import XPathSelector
from compoment.atx2agent.core.common.logs.log_uru import Logger
from compoment.atx2agent.core.core_test.constant import TEST_PIC
from compoment.atx2agent.core.task.task_manage import Device
from compoment.atx2agent.core.tools.cvtools import imread
from compoment.atx2agent.core.tools.picoperator import Template

logger = Logger().get_logger


def create_driver(serial):
    """
    # 创建设备对象并连接一个设备
    :param device_id:
    :return:
    @param serial:
    """
    try:
        try:
            return uiautomator2.connect(serial)
        except ImportError:
            raise ImportError("Please install uiautomator2: pip3 install uiautomator2")
    except ServerError:
        raise ServerError("Please start atx-agent: adb shell atx-agent")


def convert_to_camel_case(name):
    """
    将下划线命名法转换为驼峰命名法
    :param name:
    :return:
    """
    components = name.split("_")
    return "".join(x.title() for x in components)


def get_device_info(device):
    """
    获取设备信息
    :param device:
    :return:
    """
    logger.debug(
        f"Phone Name: {device.get_info()['productName']}, SDK Version: {device.get_info()['sdkInt']}"
    )
    if int(device.get_info()["sdkInt"]) < 19:
        logger.warning("Only Android 4.4+ (SDK 19+) devices are supported!")
    logger.debug(
        f"Screen dimension: {device.get_info()['displayWidth']}x{device.get_info()['displayHeight']}"
    )
    logger.debug(
        f"Screen resolution: {device.get_info()['displaySizeDpX']}x{device.get_info()['displaySizeDpY']}"
    )
    logger.debug(f"Device ID: {device.deviceV2.serial}")


class StepType(Enum):
    """
    步骤类型
    """
    INFO = 1
    PASS = 2
    WARN = 3
    ERROR = 4


class Timeout(Enum):
    """
    超时枚举类
    """
    ZERO = auto()
    TINY = auto()
    SHORT = auto()
    MEDIUM = auto()
    LONG = auto()


class SleepTime(Enum):
    """
    睡眠时间枚举类
    """
    ZERO = auto()
    TINY = auto()
    SHORT = auto()
    DEFAULT = auto()


class Location(Enum):
    """
    定位方式枚举类
    """
    CUSTOM = auto()
    WHOLE = auto()
    CENTER = auto()
    BOTTOM = auto()
    RIGHT = auto()
    LEFT = auto()
    BOTTOMRIGHT = auto()
    LEFTEDGE = auto()
    RIGHTEDGE = auto()
    TOPLEFT = auto()


class Direction(Enum):
    """
    滑动方向枚举类
    """
    UP = auto()
    DOWN = auto()
    RIGHT = auto()
    LEFT = auto()


class Mode(Enum):
    """
    输入方式模式枚举类
    """
    TYPE = auto()
    PASTE = auto()


def random_sleep(param, param1):
    """
    随机睡眠
    :param param:
    :param param1:
    :return:
    """
    sleep(uniform(param, param1))


class Locator:
    """
    页面元素封装
    """

    def __init__(self, element, wait_sec=3, by_type='id', locator_name='', desc=''):
        """

        @param element: 定位语句
        @param wait_sec: 等待时间 默认3秒
        @param by_type: 定位方式
        @param locator_name: 变量名
        @param desc: 描述
        """
        self.element = element
        self.wait_sec = wait_sec
        self.by_type = by_type
        self.locator_name = locator_name
        self.desc = desc

    def __str__(self):
        return f'{self.desc}:(By:{self.by_type},element:{self.element})'

    def __repr__(self):
        return f'{self.desc}'




class BasePage:
    # 初始化 连接设备
    def __init__(self, driver=None, device: Device = None, path=None, file_name=None):
        """
        初始化元素定位对象
        @param device:
        @param path:
        @param file_name:
        """
        logger.info("初始化设备对象:{}".format(device))
        self.device = device
        self.deviceV2 = driver
        self.global_params = {}
        self.start_time = time.time()
        self.time_out = 10
        self.path = path
        self.file_name = file_name  # or os.path.splitext(os.path.split(path)[-1])[0]
        self.data_dict = self._parse_yaml()
        self._locator_map = self.read_yaml()
        self.width,self.height= self.get_windowsize()

    def get_windowsize(self):
        '''
        获取屏幕尺寸
        :return: width,height
        '''
        window_size = self.deviceV2.window_size()
        width = int(window_size[0])
        height = int(window_size[1])
        return width, height

    def _parse_yaml(self):
        """
        读取Yaml文件内容
        :return:
        """
        data_dict = {}
        try:
            with open(self.path, 'r+', encoding='utf-8') as f:
                data_dict = yaml.load(f, Loader=yaml.FullLoader) or {}
        except Exception as e:
            raise Exception(e)
        finally:
            return data_dict

    def read_yaml(self):
        """
        页面元素定位
        :return:
        """
        pages_list = self.data_dict["pages"]
        locator_map = dict()
        for page in pages_list:
            page_name = page["page"]["pageName"]
            page_desc = page["page"]["desc"]
            locator_map[page_name] = dict()
            locators_list = page["page"]["locators"]
            for locator in locators_list:
                by_type = locator["type"]
                element = locator["value"]
                wait_sec = int(locator.get("timeout", 3))
                locator_name = locator["name"]
                desc = f"{page_desc}_{locator['desc']}"
                tmp = Locator(element, wait_sec, by_type, locator_name, desc)
                locator_map[page_name][locator_name] = tmp
        return locator_map

    def __getattr__(self, item):
        if "_locator_map" in dir(self) and "file_name" in dir(self):
            if item in self._locator_map[self.file_name]:
                locator = self.get_locator(item)
                if locator:
                    return locator
                else:
                    return self[item]

    def create_code(self):
        for k, v in self.read_yaml()[self.file_name].items():
            logger.info(f'''
            @property
            def {k}(self):
                """
                {v}
                """
                return self.get_locator("{k}")
            ''')

    @staticmethod
    def navigate_to_page(page_name):
        page_class = BasePage.page_registry.get(page_name)
        if page_class is None:
            raise ValueError(f"{page_name} is not a registered page.")
        return page_class()

    @classmethod
    def register_page(cls, page_name):
        BasePage.page_registry[page_name] = cls

    def nav_to_page(self, page_object):
        self.page = page_object
        return self.page

    # 下拉通知栏
    def notification_down(self):
        self.swipe_points(550, 0, 500, 800)

    def _get_current_app(self):
        """
        获取当前app的包名
        :return:
        """
        try:
            return self.deviceV2.app_current()["package"]
        except uiautomator2.JSONRPCError as e:
            raise BasePage.JsonRpcError(e)

    def get_locator(self, locator_name):
        """
        获取元素定位
        @param locator_name:
        @return:
        """
        locator = self._locator_map.get(self.file_name)
        if locator:
            locator = locator.get(locator_name)
        return locator

    @staticmethod
    def _get_locator_tuple(locator):
        """
        获取元素定位元组 (by_type, element)
        @param locator:
        @return:
        """
        # TODO 获取元素定位元组 (by_type, element)
        type_dict = {
            "text": "text",  # MASK_TEXT,
            "textContains": "textContains",  # MASK_TEXTCONTAINS,
            "textMatches": "textMatches",  # MASK_TEXTMATCHES,
            "textStartsWith": "textStartsWith",  # MASK_TEXTSTARTSWITH,
            "className": "className",  # MASK_CLASSNAME
            "classNameMatches": "classNameMatches",  # MASK_CLASSNAMEMATCHES
            "description": "description",  # MASK_DESCRIPTION
            "descriptionContains": "descriptionContains",  # MASK_DESCRIPTIONCONTAINS
            "descriptionMatches": "descriptionMatches",  # MASK_DESCRIPTIONMATCHES
            "descriptionStartsWith": "descriptionStartsWith",  # MASK_DESCRIPTIONSTARTSWITH
            "checkable": "checkable",  # MASK_CHECKABLE
            "checked": "checked",  # MASK_CHECKED
            "clickable": "clickable",  # MASK_CLICKABLE
            "longClickable": "longClickable",  # MASK_LONGCLICKABLE,
            "scrollable": "scrollable",  # MASK_SCROLLABLE,
            "enabled": "enabled",  # MASK_ENABLED,
            "focusable": "focusable",  # MASK_FOCUSABLE,
            "focused": "focused",  # MASK_FOCUSED,
            "selected": "selected",  # MASK_SELECTED,
            "packageName": "packageName",  # MASK_PACKAGENAME,
            "packageNameMatches": "packageNameMatches",  # MASK_PACKAGENAMEMATCHES,
            "resourceId": "resourceId",  # MASK_RESOURCEID,
            "resourceIdMatches": "resourceIdMatches",  # MASK_RESOURCEIDMATCHES,
            "index": "index",  # MASK_INDEX,
            "instance": "instance",  # MASK_INSTANCE,
            "xpath": "xpath",
            "Template": Template
        }
        locator_t = {type_dict[locator.by_type]: locator.element}
        return locator_t

    # 返回view 对象
    @allure.step("查找元素：{locator}")
    def find_element(self, locator):
        ele = self._get_element(locator)
        return ele

    @allure.step("查找多个元素：{locator}")
    def find_elements(self, locator):
        self.wait_for(locator.wait_sec)
        eles = self._get_elements(locator)
        return eles

    def _get_element(self, locator):
        start_time = time.time()
        time_out = locator.wait_sec
        while True:
            try:
                value_text = locator.desc
            except:
                value_text = ""
            try:
                locator_t = self._get_locator_tuple(locator)
                if "Template" not in locator_t.keys():
                    element = self._find_element(**locator_t)
                else:
                    logger.info("使用图片比对算法进行图片坐标查找")
                    # 获取这个locator_t 字典的值
                    locator_t_template = locator_t.get("Template")
                    element = self._loop_find(Template(**eval(locator_t_template)))
                    if element is None:
                        error_msg = f'当前没有匹配到「{value_text}」图片对应的元素'
                        logger.error(error_msg)
                        # TODO  抛出uiautomator2的元素未找到的异常
                        raise UiObjectNotFoundError()
                return element
            except UiObjectNotFoundError as n:
                time.sleep(0.5)
                if time.time() - start_time >= time_out:
                    logger.error("{time_out}秒后仍没有找到元素「{value_text}」")
                    raise UiObjectNotFoundError()
            except ServerError as w:
                time.sleep(0.5)
                if time.time() - start_time >= time_out:
                    raise ServerError(f"{time_out}秒后浏览器仍异常「{value_text}」:{w}")
            except Exception as e:
                raise Exception(f"查找元素异常：{e}")

    def _get_elements(self, locator):
        locator_t = self._get_locator_tuple(locator)
        element = self.driver.find_elements(*locator_t)
        return element

    @allure.step("查看「{locator}」是否存在")
    def has_element(self, locator):
        ret = False
        try:
            ele = self.find_element(locator)
            if ele:
                ret = True
        except Exception as e:
            logger.error(f"查看元素「{locator}」是否存在异常:{e}")
        return ret

    def wait_element(self, locator, timeout=10):
        """ 等待x秒元素出现"""
        try:
            ele = self._get_element(locator)
            if ele:
                ele.wait(ui_timeout=timeout)
            return ele
        except Exception as e:
            logger.error(f"等待元素「{locator}」出现异常:{e}")
            raise e

    def _loop_find(self, query):
        """
        循环查找 图片
        @param query:
        @return:
        """
        file_name = os.path.join(TEST_PIC, f'{str(int(time.time() * 1000))}.png')
        self.screenshot(file_name)
        screen = imread(file_name)
        if screen is None:
            logger.warning("截图失败")
        else:
            match_pos = query.match_in(screen)
            if match_pos:
                return match_pos

    def _find_element(
            self,
            index=None,
            timeout=10,
            **kwargs,
    ):
        view = None
        try:
            # locator_t = (type_dict[locator.by_type], locator.element)
            if kwargs is not None:
                for key, value in kwargs.items():
                    if "xpath" in key:
                        view = self.find_by_xpath(value)
                    else:
                        if key not in getattr(Selector, "_Selector__fields"):
                            logger.error("查找元素失败，没有这个：{}元素类型！".format(key))
                            # raise AttributeError("查找元素失败，没有这个{}元素类型！".format(key))
                        view = self.deviceV2(**kwargs)
                        if index is not None and view.count > 1:
                            view = self.deviceV2(**kwargs)[index]
                if self.loop_watcher(view, timeout):
                    return BasePage.View(view=view, device=self.deviceV2)
            else:
                return None
        except Exception as e:
            logger.error("查找元素失败，没有这个：{}元素类型！，异常：{}".format(kwargs, e))

    def loop_watcher(self, view=None, timeout=10):
        """
        循环查找函数：每隔一秒，循环查找元素是否存在. 如果元素存在，click操作
        :param view: 要查找元素，需要是poco对象
        :param timeout: 超时时间，单位：秒
        :return:
        """
        logger.info("view:::::::::{}".format(view))
        start_time = time.time()
        is_exited = False
        try:
            while (time.time() - start_time) < timeout:
                logger.info("view:::::::::{}".format(view))
                # 判断是否 是UiObject对象
                if isinstance(view, UiObject):
                    if view.exists():
                        is_exited = True
                        logger.info("查询到ui元素：[{}]".format(view.selector))
                        break
                elif isinstance(view, XPathSelector):
                    if len(view.all()) > 0:
                        is_exited = True
                        logger.info("查询到xpath元素：[{}]".format(view))
                        break
                else:
                    logger.info("未查找到元素对象：{}，超时了.".format(view))
                    break
                time.sleep(1)
        except Exception as e:
            logger.error("查找元素对象：{}，失败！{}".format(view, e))
        return is_exited

    @allure.step("断言元素是否存在：{locator}")
    def assert_exited(self, locator):
        '''
        断言当前页面存在要查找的元素,存在则判断成功
        @param locator:
        @return:
        '''
        assert self.find_element_exists(locator, timeout=10) is True, "断言{}元素不存在,失败!" \
            .format(locator)
        logger.info("断言{}元素存在,成功!".format(locator))




    @allure.step("查找元素是否存在：{locator}")
    def find_element_exists(self, locator, timeout=10):
        """
        查找元素是否存在当前页面
        :return:
        """
        is_exited = False
        try:
            while timeout > 0:
                xml = self.deviceV2.dump_hierarchy()
                value = locator.element
                if re.findall(value, xml):
                    is_exited = True
                    logger.info("查询到元素：[{}]".format(value))
                    return is_exited
                else:
                    logger.info("未查询到元素.：[{}]".format(value))
                    timeout -= 1
                    time.sleep(1)
            return is_exited
        except Exception as e:
            logger.error("{}查找失败!{}".format(locator, e))

    @allure.step("查找xpath元素：{xpath}")
    def find_by_xpath(self, xpath):
        """
        通过xpath查找元素
        :param xpath:
        :return:
        """
        try:
            return self.deviceV2.xpath(xpath)
        except uiautomator2.JSONRPCError as e:
            raise BasePage.JsonRpcError(e)


    @allure.step("截图{path}")
    def screenshot(self, path):
        self.deviceV2.screenshot(path)



    def is_screen_locked(self):
        data = run(
            f"adb -s {self.deviceV2.serial} shell dumpsys window",
            encoding="utf-8",
            stdout=PIPE,
            stderr=PIPE,
            shell=True,
        )
        if data != "":
            flag = re.search("mDreamingLockscreen=(true|false)", data.stdout)
            return flag is not None and flag.group(1) == "true"
        else:
            logger.debug(
                f"'adb -s {self.deviceV2.serial} shell dumpsys window' returns nothing!"
            )
            return None

    def _is_keyboard_show(self):
        data = run(
            f"adb -s {self.deviceV2.serial} shell dumpsys input_method",
            encoding="utf-8",
            stdout=PIPE,
            stderr=PIPE,
            shell=True,
        )
        if data != "":
            flag = re.search("mInputShown=(true|false)", data.stdout)
            return flag.group(1) == "true"
        else:
            logger.debug(
                f"'adb -s {self.deviceV2.serial} shell dumpsys input_method' returns nothing!"
            )
            return None

    @allure.step("Unlock screen")
    def unlock(self):
        self.swipe(Direction.UP, 0.8)
        sleep(2)
        logger.debug(f"Screen locked: {self.is_screen_locked()}")
        if self.is_screen_locked():
            self.swipe(Direction.RIGHT, 0.8)
            sleep(2)
            logger.debug(f"Screen locked: {self.is_screen_locked()}")

    # 关闭屏幕
    @allure.step("Screen off")
    def screen_off(self):
        self.deviceV2.screen_off()

    @allure.step("Get orientation")
    def get_orientation(self):
        try:
            return self.deviceV2._get_orientation()
        except uiautomator2.JSONRPCError as e:
            raise BasePage.JsonRpcError(e)

    @allure.step("Get window size")
    def window_size(self):
        """return (width, height)"""
        try:
            self.deviceV2.window_size()
        except uiautomator2.JSONRPCError as e:
            raise BasePage.JsonRpcError(e)

    @allure.step("swipe {time}")
    def swip_down(self, time=0.5):
        """
            向上滑动
            :return:
        """
        self.deviceV2.drag(self.width / 2, self.height * 3 / 4, self.width / 2, self.height / 4, time)
        logger.info("向下滑动")

    @allure.step("swipe {time}")
    def swip_up(self, time=0.5):
        '''
        向下滑动，只适用1920*1080手机
        :return:
        '''
        self.deviceV2.drag(540, 480, 540, 1440, time)
        logger.info("向上滑动")


    @allure.step("Swipe {direction}")
    def swipe(self, direction: Direction, scale=0.5):
        """Swipe finger in the `direction`.
        Scale is the sliding distance. Default to 50% of the screen width
        """
        swipe_dir = ""
        if direction == Direction.UP:
            swipe_dir = "up"
        elif direction == Direction.RIGHT:
            swipe_dir = "right"
        elif direction == Direction.LEFT:
            swipe_dir = "left"
        elif direction == Direction.DOWN:
            swipe_dir = "down"

        logger.debug(f"Swipe {swipe_dir}, scale={scale}")

        try:
            self.deviceV2.swipe_ext(swipe_dir, scale=scale)
            BasePage.sleep_mode(SleepTime.TINY)
        except uiautomator2.JSONRPCError as e:
            raise BasePage.JsonRpcError(e)

    @allure.step("Swipe from ({sx},{sy}) to ({ex},{ey})")
    def swipe_points(self, sx, sy, ex, ey, random_x=True, random_y=True):
        if random_x:
            sx = int(sx * uniform(0.85, 1.15))
            ex = int(ex * uniform(0.85, 1.15))
        if random_y:
            ey = int(ey * uniform(0.98, 1.02))
        sy = int(sy)
        try:
            logger.debug(f"Swipe from: ({sx},{sy}) to ({ex},{ey}).")
            self.deviceV2.swipe_points([[sx, sy], [ex, ey]], uniform(0.2, 0.5))
            BasePage.sleep_mode(SleepTime.TINY)
        except uiautomator2.JSONRPCError as e:
            raise BasePage.JsonRpcError(e)

    @allure.step("获取设备信息")
    def get_device_info(self):
        # {'currentPackageName': 'net.oneplus.launcher', 'displayHeight': 1920, 'displayRotation': 0, 'displaySizeDpX': 411,
        # 'displaySizeDpY': 731, 'displayWidth': 1080, 'productName': 'OnePlus5', '
        #  screenOn': True, 'sdkInt': 27, 'naturalOrientation': True}
        try:
            return self.deviceV2.info
        except uiautomator2.JSONRPCError as e:
            raise BasePage.JsonRpcError(e)

    # 获取元素信息
    def get_info(self, locator):
        ele = self.find_element(locator)
        return ele.ui_info()

    @allure.step("打开app: {package_name} {activity}")
    def open_app(self, package_name, activity):
        self.deviceV2.app_start(package_name, activity)

    def handler_exception(self, by_type="mobile_xpath", sys='android', need_break=True, source=''):
        """
        通用弹框处理
        @return:
        """
        _blank_list = [
            Locator("//*[@text='同意']", wait_sec=0, by_type=by_type, desc="同意"),
            Locator("//*[contains(@text,'允许')]", wait_sec=0, by_type=by_type, desc="允许"),
            Locator("//*[@text='确定']", wait_sec=0, by_type=by_type, desc="确定"),
            Locator("//*[@text='稍后再说']", wait_sec=0, by_type=by_type, desc="稍后再说"),
            Locator("//*[@text='以后再说']", wait_sec=0, by_type=by_type, desc="以后再说"),
            Locator("//*[@text='我知道了']", wait_sec=0, by_type=by_type, desc="我知道了"),
            Locator("//*[@text='仅在使用中允许']", wait_sec=0, by_type=by_type, desc="仅在使用中允许"),
            Locator("//*[@text='我知道啦']", wait_sec=0, by_type=by_type, desc="我知道啦"),
            Locator("//*[@text='始终允许']", wait_sec=0, by_type=by_type, desc="始终允许"),
            Locator("//*[@text='仍然视频问诊']", wait_sec=0, by_type=by_type, desc="仍然视频问诊"),
            Locator("//*[@text='知道了']", wait_sec=0, by_type=by_type, desc="知道了")
        ]
        if by_type == 'xpath':
            # H5的弹框关闭
            _blank_list += [
                Locator('//div[@class="wand-dialog-img__close"]', wait_sec=0, by_type=by_type, desc="关闭按钮"),
            ]
        if by_type == "mobile_xpath" and sys == "android":
            # 安卓APP的弹框关闭
            _blank_list += [
                Locator("//android.widget.ImageView[@content-desc='关闭']", wait_sec=0, by_type=by_type, desc="关闭"),

            ]
        if by_type == "mobile_xpath" and sys == "ios":
            # ios APP的弹框关闭
            _blank_list += [
                Locator("//XCUIElementTypeButton[@name='web rontview close']", wait_sec=0, by_type=by_type,
                        desc="关闭"),
                Locator("//XCUIElementTypeImage[@name='icon_consult_coupon_dismiss']", wait_sec=0, by_type=by_type,
                        desc="关闭弹窗"),
                Locator("//XCUIElementTypeButton[@name='好']", wait_sec=0, by_type=by_type, desc="权限弹窗-好"),
                Locator("//XCUIElementTypeButton[@name='取消']", wait_sec=0, by_type=by_type, desc="权限弹窗-取消"),
                Locator("//XCUIElementTypeButton[@name='以后']", wait_sec=0, by_type=by_type, desc="权限弹窗-以后"),

            ]
        if source == 'local':
            _blank_list += [
                # 需要区分场景（有些页面图片可点击，导致误点）
                Locator("//*[@resource-id='android:id/content']//android.widget.ImageView", wait_sec=0,
                        by_type=by_type,
                        desc="浮层"),
            ]
        logger.info("+++++++++++++通用弹框处理+++++++++++++")
        for index, loc in enumerate(_blank_list):
            try:
                self.click(loc)
                logger.info(f"找到了 {loc},并且已点击")
                if need_break:
                    if index != len(_blank_list) - 1:
                        self.has_element(_blank_list[index + 1])
                        continue
                    else:
                        break
            except Exception as e:
                e = str(e).replace('\n', '')
                logger.info(f"未找到『{loc.desc}』:{e}")
                pass

    @allure.step("点击「{locator}」")
    def click(self, locator, num=0, special=0):
        """
        点击  0:普通点击 1:双击
        @param locator:
        @param num:
        @param special:
        @return:
        """
        ele = self.find_element(locator)
        if isinstance(ele, tuple):
            if isinstance(self.driver, uiautomator2.Device):
                self.driver2.tap([ele], 500)
        else:
            if special == 0:
                ele.click()
            elif special == 1:
                ele.double_click()

    @allure.step("往「{locator}」输入「{msg}」")
    def input(self, locator, msg, num=0, clear=True):
        ele = self.find_element(locator)
        logger.info(f"往「{locator.desc}」输入「{msg}」")
        try:
            ele.set_text(msg)
        except Exception as e:
            logger.error(f"往「{locator}」输入「{msg}」失败:{e}")
        time.sleep(0.2)

    @allure.step("获取「{locator}」的文本")
    def get_text(self, locator):
        ele = self.find_element(locator)
        return ele.get_text()

    class View:
        deviceV2 = None  # uiautomator2
        viewV2 = None  # uiautomator2

        def __init__(self, view, device):
            self.viewV2 = view
            self.deviceV2 = device

        def __iter__(self):
            children = []
            try:
                children.extend(
                    BasePage.View(view=item, device=self.deviceV2)
                    for item in self.viewV2
                )
                return iter(children)
            except uiautomator2.JSONRPCError as e:
                raise BasePage.JsonRpcError(e)

        @allure.step("获取ui2对象的info信息")
        def ui_info(self):
            try:
                return self.viewV2.info
            except uiautomator2.JSONRPCError as e:
                raise BasePage.JsonRpcError(e)

        @allure.step("获取ui2对象的描述信息")
        def content_desc(self):
            try:
                return self.viewV2.info["contentDescription"]
            except uiautomator2.JSONRPCError as e:
                raise BasePage.JsonRpcError(e)

        # 子元素定位
        @allure.step("获取元素的子元素{args} {kwargs}")
        def child(self, *args, **kwargs):
            try:
                view = self.viewV2.child(*args, **kwargs)
            except uiautomator2.JSONRPCError as e:
                raise BasePage.JsonRpcError(e)
            return BasePage.View(view=view, device=self.deviceV2)

        # 兄弟元素定位
        @allure.step("获取元素的兄弟元素{args} {kwargs}")
        def sibling(self, *args, **kwargs):
            try:
                view = self.viewV2.sibling(*args, **kwargs)
            except uiautomator2.JSONRPCError as e:
                raise BasePage.JsonRpcError(e)
            return BasePage.View(view=view, device=self.deviceV2)

        # 某个元素的左边相对定位
        @allure.step("获取元素的左边元素{args} {kwargs}")
        def left(self, *args, **kwargs):
            try:
                view = self.viewV2.left(*args, **kwargs)
            except uiautomator2.JSONRPCError as e:
                raise BasePage.JsonRpcError(e)
            return BasePage.View(view=view, device=self.deviceV2)

        # 某个元素的右边相对定位
        @allure.step("获取元素的右边元素{args} {kwargs}")
        def right(self, *args, **kwargs):
            try:
                view = self.viewV2.right(*args, **kwargs)
            except uiautomator2.JSONRPCError as e:
                raise BasePage.JsonRpcError(e)
            return BasePage.View(view=view, device=self.deviceV2)

        @allure.step("获取元素的上边元素{args} {kwargs}")
        def up(self, *args, **kwargs):
            try:
                view = self.viewV2.up(*args, **kwargs)
            except uiautomator2.JSONRPCError as e:
                raise BasePage.JsonRpcError(e)
            return BasePage.View(view=view, device=self.deviceV2)

        @allure.step("获取元素的下边元素{args} {kwargs}")
        def down(self, *args, **kwargs):
            try:
                view = self.viewV2.down(*args, **kwargs)
            except uiautomator2.JSONRPCError as e:
                raise BasePage.JsonRpcError(e)
            return BasePage.View(view=view, device=self.deviceV2)

        @allure.step("点击重试「{maxretry}」次，间隔「{interval}」秒")
        def click_gone(self, maxretry=3, interval=1.0):
            try:
                self.viewV2.click_gone(maxretry, interval)
            except uiautomator2.JSONRPCError as e:
                raise BasePage.JsonRpcError(e)

        @allure.step("点击「{mode},{sleep},{coord}」")
        def click(self, mode=None, sleep=None, coord=None, crash_report_if_fails=True):

            global x_offset , y_offset
            if coord is None:
                coord = []
            mode = Location.WHOLE if mode is None else mode
            if mode == Location.WHOLE:
                x_offset = uniform(0.15, 0.85)
                y_offset = uniform(0.15, 0.85)

            elif mode == Location.LEFT:
                x_offset = uniform(0.15, 0.4)
                y_offset = uniform(0.15, 0.85)

            elif mode == Location.LEFTEDGE:
                x_offset = uniform(0.1, 0.2)
                y_offset = uniform(0.40, 0.60)

            elif mode == Location.CENTER:
                x_offset = uniform(0.4, 0.6)
                y_offset = uniform(0.15, 0.85)

            elif mode == Location.RIGHT:
                x_offset = uniform(0.6, 0.85)
                y_offset = uniform(0.15, 0.85)

            elif mode == Location.RIGHTEDGE:
                x_offset = uniform(0.8, 0.9)
                y_offset = uniform(0.40, 0.60)

            elif mode == Location.BOTTOMRIGHT:
                x_offset = uniform(0.8, 0.9)
                y_offset = uniform(0.8, 0.9)

            elif mode == Location.TOPLEFT:
                x_offset = uniform(0.05, 0.15)
                y_offset = uniform(0.05, 0.25)
            elif mode == Location.CUSTOM:
                try:
                    logger.debug(f"Single click ({coord[0]},{coord[1]})")
                    self.deviceV2.click(coord[0], coord[1])
                    BasePage.sleep_mode(sleep)
                    return
                except uiautomator2.JSONRPCError as e:
                    if crash_report_if_fails:
                        raise BasePage.JsonRpcError(e)
                    else:
                        logger.debug("试图点击一个已经消失的对象.")
            else:
                x_offset = 0.5
                y_offset = 0.5

            try:
                visible_bounds = self.get_bounds()
                x_abs = int(
                    visible_bounds["left"]
                    + (visible_bounds["right"] - visible_bounds["left"]) * x_offset
                )
                y_abs = int(
                    visible_bounds["top"]
                    + (visible_bounds["bottom"] - visible_bounds["top"]) * y_offset
                )

                logger.debug(
                    f"Single click in ({x_abs},{y_abs}). Surface: ({visible_bounds['left']}-{visible_bounds['right']},{visible_bounds['top']}-{visible_bounds['bottom']})"
                )
                if isinstance(self.viewV2, uiautomator2.UiObject):
                    self.viewV2.click(
                        self.get_ui_timeout(Timeout.LONG),  # TODO 为什么这里要用长超时？
                        offset=(x_offset, y_offset),
                    )
                elif isinstance(self.viewV2,XPathSelector):
                    self.viewV2.click(
                        self.get_ui_timeout(Timeout.LONG),  # TODO 为什么这里要用长超时？
                    )
                BasePage.sleep_mode(sleep)

            except uiautomator2.JSONRPCError as e:
                if crash_report_if_fails:
                    raise BasePage.JsonRpcError(e)
                else:
                    logger.debug("试图点击一个已经消失的对象.")

        @allure.step("点击重试「{maxretry}」次")
        def click_retry(self, mode=None, sleep=None, coord=None, maxretry=2):
            """return True if successfully open the element, else False"""
            if coord is None:
                coord = []
            self.click(mode, sleep, coord)

            while maxretry > 0:
                # we wait a little more before try again
                random_sleep(0.5, 1.0)
                if not self.exists():
                    return True
                logger.debug("UI element didn't open! Try again..")
                self.click(mode, sleep, coord)
                maxretry -= 1
            if not self.exists():
                return True
            logger.warning("Failed to open the UI element!")
            return False

        @allure.step("双击{padding},{obj_over}")
        def double_click(self, padding=0.3, obj_over=0):
            """Double click randomly in the selected view using padding
            padding: % of how far from the borders we want the double
                    click to happen.
            """
            visible_bounds = self.get_bounds()
            horizontal_len = visible_bounds["right"] - visible_bounds["left"]
            vertical_len = visible_bounds["bottom"] - max(
                visible_bounds["top"], obj_over
            )
            horizontal_padding = int(padding * horizontal_len)
            vertical_padding = int(padding * vertical_len)
            random_x = int(
                uniform(
                    visible_bounds["left"] + horizontal_padding,
                    visible_bounds["right"] - horizontal_padding,
                )
            )
            random_y = int(
                uniform(
                    visible_bounds["top"] + vertical_padding,
                    visible_bounds["bottom"] - vertical_padding,
                )
            )

            time_between_clicks = uniform(0.050, 0.140)

            try:
                logger.debug(
                    f"Double click in ({random_x},{random_y}) with t={int(time_between_clicks * 1000)}ms. Surface: ({visible_bounds['left']}-{visible_bounds['right']},{visible_bounds['top']}-{visible_bounds['bottom']})."
                )
                self.deviceV2.double_click(
                    random_x, random_y, duration=time_between_clicks
                )
                BasePage.sleep_mode(SleepTime.DEFAULT)
            except uiautomator2.JSONRPCError as e:
                raise BasePage.JsonRpcError(e)

        @allure.step("滚动到{direction}位置")
        def scroll(self, direction):
            try:
                if direction == Direction.UP:
                    self.viewV2.scroll.toBeginning(max_swipes=1)
                else:
                    self.viewV2.scroll.toEnd(max_swipes=1)
            except uiautomator2.JSONRPCError as e:
                raise BasePage.JsonRpcError(e)

        @allure.step("fling {direction} 位置")
        def fling(self, direction):
            try:
                if direction == Direction.UP:
                    self.viewV2.fling.toBeginning(max_swipes=5)
                else:
                    self.viewV2.fling.toEnd(max_swipes=5)
            except uiautomator2.JSONRPCError as e:
                raise BasePage.JsonRpcError(e)

        @property
        def width(self):
            """
            获取屏幕宽度
            """
            return self.viewV2.info["displayWidth"]

        @property
        def height(self):
            """
            获取屏幕高度
            """
            return self.viewV2.info["displayHeight"]

        @allure.step("点击坐标「{x_size}」「{y_size}」所在的位置")
        def click_point(self, x_size, y_size):
            x = self.width * x_size
            y = self.height * y_size
            self.viewV2.tap([(x, y)])

        # 检查对象是否存在于当前窗口
        @allure.step("检查元素是否存在于当前窗口")
        def exists(self, ui_timeout=None, ignore_bug: bool = False) -> bool:
            try:
                # Currently, the methods left, right, up and down from
                # uiautomator2 return None when a Selector does not exist.
                # All other selectors return an UiObject with exists() == False.
                # We will open a ticket to uiautomator2 to fix this inconsistency.
                if self.viewV2 is None:
                    return False
                exists: bool = self.viewV2.exists(self.get_ui_timeout(ui_timeout))
                if (
                        hasattr(self.viewV2, "count")
                        and not exists
                        and self.viewV2.count >= 1
                ):
                    logger.debug(
                        f"UIA2 BUG: exists return False, but there is/are {self.viewV2.count} element(s)!"
                    )
                    if ignore_bug:
                        return "BUG!"
                    # More info about that: https://github.com/openatx/uiautomator2/issues/689"
                    return False
                return exists
            except uiautomator2.JSONRPCError as e:
                raise BasePage.JsonRpcError(e)

        def count_items(self) -> int:
            try:
                return self.viewV2.count
            except uiautomator2.JSONRPCError as e:
                raise BasePage.JsonRpcError(e)

        @allure.step("等待「{ui_timeout}」时间")
        def wait(self, ui_timeout=10):
            try:
                return self.viewV2.wait(timeout=ui_timeout)
            except uiautomator2.JSONRPCError as e:
                logger.error(f"UI element not found: {e}")
                raise UiObjectNotFoundError()

        @allure.step("等待「{ui_timeout}」时间元素消失.")
        def wait_gone(self, ui_timeout=None):
            try:
                return self.viewV2.wait_gone(timeout=self.get_ui_timeout(ui_timeout))
            except uiautomator2.JSONRPCError as e:
                raise BasePage.JsonRpcError(e)

        def is_above_this(self, obj2) -> Optional[bool]:
            obj1 = self.viewV2
            obj2 = obj2.viewV2
            try:
                if obj1.exists() and obj2.exists():
                    return obj1.info["bounds"]["top"] < obj2.info["bounds"]["top"]
                else:
                    return None
            except uiautomator2.JSONRPCError as e:
                raise BasePage.JsonRpcError(e)

        def get_bounds(self) -> dict:
            try:
                return self.viewV2.info["bounds"]
            except uiautomator2.JSONRPCError as e:
                raise BasePage.JsonRpcError(e)

        def get_height(self) -> int:
            bounds = self.get_bounds()
            return bounds["bottom"] - bounds["top"]

        def get_width(self):
            bounds = self.get_bounds()
            return bounds["right"] - bounds["left"]

        def get_property(self, prop: str):
            try:
                return self.viewV2.info[prop]
            except uiautomator2.JSONRPCError as e:
                raise BasePage.JsonRpcError(e)

        @staticmethod
        def get_ui_timeout(ui_timeout: Timeout) -> int:
            ui_timeout = Timeout.ZERO if ui_timeout is None else ui_timeout
            if ui_timeout == Timeout.ZERO:
                ui_timeout = 0
            elif ui_timeout == Timeout.TINY:
                ui_timeout = 1
            elif ui_timeout == Timeout.SHORT:
                ui_timeout = 3
            elif ui_timeout == Timeout.MEDIUM:
                ui_timeout = 5
            elif ui_timeout == Timeout.LONG:
                ui_timeout = 8
            return ui_timeout

        @allure.step("获取文本")
        def get_text(self, error=True, index=None):
            try:
                text = (
                    self.viewV2.info["text"]
                    if index is None
                    else self.viewV2[index].info["text"]
                )
                if text is not None:
                    return text
            except uiautomator2.JSONRPCError as e:
                if error:
                    raise BasePage.JsonRpcError(e)
                else:
                    return ""
            logger.debug("Object exists but doesn't contain any text.")
            return ""

        def get_selected(self) -> bool:
            try:
                if self.viewV2.exists():
                    return self.viewV2.info["selected"]
                logger.debug(
                    "Object has disappeared! Probably too short video which has been liked!"
                )
                return True
            except uiautomator2.JSONRPCError as e:
                raise BasePage.JsonRpcError(e)



        @allure.step("输入「{text}」")
        def set_text(self, text: str, mode: Mode = Mode.TYPE) -> None:
            """
            设置元素文本
            :param text: 文本内容
            :param mode:
            :return:
            """
            punct_list = string.punctuation
            try:
                if mode == Mode.PASTE:
                    self.viewV2.set_text(text)
                else:
                    self.click(sleep=SleepTime.SHORT)
                    self.deviceV2.clear_text()
                    random_sleep(0.3, 1)
                    start = datetime.now()
                    sentences = text.splitlines()
                    for j, sentence in enumerate(sentences, start=1):
                        word_list = sentence.split()
                        n_words = len(word_list)
                        for n, word in enumerate(word_list, start=1):
                            i = 0
                            n_single_letters = randint(1, 3)
                            for char in word:
                                if i < n_single_letters:
                                    self.deviceV2.send_keys(char, clear=False)
                                    # random_sleep(0.01, 0.1, modulable=False, logging=False)
                                    i += 1
                                else:
                                    if word[-1] in punct_list:
                                        self.deviceV2.send_keys(word[i:-1], clear=False)
                                        # random_sleep(0.01, 0.1, modulable=False, logging=False)
                                        self.deviceV2.send_keys(word[-1], clear=False)
                                    else:
                                        self.deviceV2.send_keys(word[i:], clear=False)
                                    # random_sleep(0.01, 0.1, modulable=False, logging=False)
                                    break
                            if n < n_words:
                                self.deviceV2.send_keys(" ", clear=False)
                                # random_sleep(0.01, 0.1, modulable=False, logging=False)
                        if j < len(sentences):
                            self.deviceV2.send_keys("\n")

                    typed_text = self.viewV2.get_text()
                    if typed_text != text:
                        logger.warning(
                            "Failed to write in text field, let's try in the old way.."
                        )
                        self.viewV2.set_text(text)
                    else:
                        logger.debug(
                            f"Text typed in: {(datetime.now() - start).total_seconds():.2f}s"
                        )
                BasePage.sleep_mode(SleepTime.SHORT)
            except uiautomator2.JSONRPCError as e:
                logger.error(f"输入「{text}」失败:{e}")

    class JsonRpcError(Exception):
        pass

    class AppHasCrashed(Exception):
        pass

    @staticmethod
    def sleep_mode(mode):
        mode = SleepTime.DEFAULT if mode is None else mode
        if mode == SleepTime.DEFAULT:
            random_sleep(0, 0.5)
        elif mode == SleepTime.TINY:
            random_sleep(0, 1)
        elif mode == SleepTime.SHORT:
            random_sleep(1, 2)
        elif mode == SleepTime.ZERO:
            pass


# 权重值验证
def validate_weights(func):
    def wrapper(self):
        if sum(self.weights.values()) != 1:
            raise ValueError("Error: Weights must sum to 1.")
        return func(self)

    return wrapper


class PageObject(BasePage):
    # 生成的页面对象基类，所有页面对象都继承自该类，包括一些基本的属性
    def __init__(self, driver=None, device=None, path=None, file_name=None, factors=None, weights=None):
        super().__init__(driver, device, path, file_name)
        self.driver = driver
        self.device = device
        self.factors = factors  # 因子
        self.weights = weights if weights is not None else {}  # 权重
        self.action_hits = {action: 0 for action in self.weights.keys()}  # 初始化执行

    def navigate_to_page(self, page_object):
        self.page = page_object
        # 默认跳转到每个页面的首页
        return self.page

    @validate_weights
    def select_action(self):
        choices = list(self.weights.keys())
        probs = list(self.weights.values())
        # chosen_action = random.choices(choices, probs)[0]
        chosen_action = np.random.choice(choices, p=probs)
        if chosen_action in self.action_hits:
            self.action_hits[chosen_action] += 1
        else:
            self.action_hits[chosen_action] = 1
        return getattr(self, chosen_action)

    def get_action_statistics(self):
        """
        获取权重执行统计信息
        @return:
        """
        total_trials = sum(self.action_hits.values())
        action_statistics = {}
        for action, num_hits in self.action_hits.items():
            action_statistics[action] = round(num_hits / total_trials * 100, 2)
        return action_statistics

    def select(self):
        """
        根据权重配置，选择一个场景
        @return:
        """
        scenes = list(self.factors.keys())
        weights = list(self.factors.values())
        # chosen_scene = random.choices(scenes, weights)[0]
        chosen_scene = np.random.choice(scenes, p=weights)

        return chosen_scene

    def run_trials(self, num_trials, page_objects):
        """
        执行权重测试
        @param num_trials:  总共运行多少次
        @param page_objects:  运行的页面对象
        @return:
        """
        results = {scene: 0 for scene in self.factors.keys()}  # 初始化执行结果
        page_probabilities = {}  # 页面配置
        for i in range(num_trials):
            chosen_scene = self.select()
            if chosen_scene not in page_objects:
                print(f"Error: Unrecognized scene name: {chosen_scene}")
                continue
            scene_page_object = page_objects[chosen_scene]
            action = scene_page_object.select_action()
            action()
            results[chosen_scene] += 1
            page_probabilities[chosen_scene] = scene_page_object.get_action_statistics()
        total_trials = sum(results.values())
        self.__calculate_percentages(results, total_trials)
        return results, page_probabilities

    def __calculate_percentages(self, results, total_trials):
        for scene, num_hits in results.items():
            results[scene] = round(num_hits / total_trials * 100, 2)

    def get_locator_by_name(self, name):
        """
        通过元素的名称返回元素对象
        :param name:
        :return:
        """
        return next((loc for loc in self.locators if loc.name == name), None)

    # 将多个字典合并成一个字典
    def merge_dict(self, *dicts):
        result = {}
        for dictionary in dicts:
            result.update(dictionary)
        return result

    def __repr__(self):
        return f"<{self.__class__.__name__}>"

    def __str__(self):
        return f"<{self.__class__.__name__}>"
