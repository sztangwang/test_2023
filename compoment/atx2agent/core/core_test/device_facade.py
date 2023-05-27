import base64
import re
import string
import time
from datetime import datetime
from enum import Enum, auto
from inspect import stack
from os import getcwd, listdir
from random import randint, uniform
from re import search
from subprocess import PIPE, run
from time import sleep
from typing import Optional

import requests
import uiautomator2
from adbutils import adb
from uiautomator2 import Selector, UiObject
from uiautomator2.xpath import XPathSelector

from compoment.atx2agent.core.common.logs.log_uru import Logger
from compoment.atx2agent.core.tools.driver_utils import random_sleep

logger = Logger().get_logger

# 设备号，通过 conftest.py 文件读取来自命令行的参数
SN = None
ENV =None

def create_device(driver):
    """
    # 创建设备对象并连接一个设备
    :param driver:
    :return:
    """
    try:
        return DeviceFacade(driver)
    except ImportError as e:
        logger.error(str(e))
        return None


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

class DeviceFacade:
    # 初始化 连接设备
    def __init__(self, device=None):
        logger.info("初始化设备对象:{}".format(device))
        # 将device 转换为 Device对象
        _device = adb.device(device)
        self.device = _device
        self.vars = {}  # 存放临时变量
        self.global_params = {}
        self.start_time = time.time()
        self.udid = ""
        try:
            if device is None or "." not in device:
                self.deviceV2 = uiautomator2.connect(
                    "" if device is None else device
                )
            else:
                self.deviceV2 = uiautomator2.connect_adb_wifi(f"{device}")
        except ImportError:
            raise ImportError("Please install uiautomator2: pip3 install uiautomator2")


    def k_click(self,locator=None):
        logger.info("元素定位{}".format(locator))
        self.find_element_view(**locator).click()

    def k_right_swipe(self):
        self.swipe_points(2, 400, 500, 400)  # 从界面的边缘滑动到界面的中间

    def k_input(self,locator=None,value=None):
        self.find_element_view(**locator).set_text(value,mode=Mode.PASTE)

    # 点击屏幕任意位置
    def k_click_screen(self,x,y):
        cmd = "input tap {0} {1}".format(x, y)
        self.device.shell(cmd)

    # 下拉通知栏
    def k_notification(self,seconds=0.5):
        sleep(seconds)
        self.swipe_points(550, 0, 500, 800)
        sleep(seconds)


    def k_open(self,packageName,activityName):
        if activityName is not None:
            self.deviceV2.app_start(packageName,activityName)
        self.app_start(packageName)

    def k_swipe_up(self):
        self.swipe(Direction.UP)
        time.sleep(1.5)


    def k_close(self,packageName):
        self.deviceV2.app_stop(packageName)


    def k_wait(self,senconds):
        self.deviceV2.sleep(senconds)

    def k_assert_text(self, locator, expect_text, element_type='text', assert_type="element"):
        '''
        断言元素文本包含指定值
        :param locator: 元素定位
        :param expect_text: 预期文本
        :param info_type: 元素信息类型
        :param assert_type: 断言类型
        :return: 断言结果
        info_type :className,resourceName,text,contentDescription
        '''
        text = ''
        try:
            if assert_type == "element":  # 元素获取元素属性断言
                text = self.find_element_view(**locator).get_text()
                self.assert_equal(expect_text, text)
            elif assert_type == "toast":  # 获取toast消息断言
                text = self.get_toast()
                self.assert_equal(expect_text, text)
            result = expect_text in str(text)
            logger.info('元素{}文本预期为"{}"，实际为"{}"，用例执行结果为- [{}]'.format(locator, expect_text, text, result))
        except:
            logger.error("{}-获取元素文本失败，用例执行失败！！！".format(locator))
            assert False

    def get_screenshot_as_png(self):
        # 截图，返回图片的二进制数据
        return self.deviceV2.screenshot(format="raw")


    # def run_action(self, action, locator, **kwargs):
    #     logger.info("action ---> {0},locator ---> {1} ,**kwargs---->{2}".format(action,locator, kwargs))
    #     action_name = "k_" + action
    #     params = {}
    #     if hasattr(self, action_name):
    #         # 判断传入的参数是否为空来执行哪一种带参的函数
    #         fun = getattr(self, action_name)
    #         logger.info("执行步骤.......：" + action_name)
    #         if kwargs is not None:
    #             # 取出 params key的值
    #             params = kwargs.get("params")
    #             logger.info("params----->{}".format(params))
    #         if len(locator)<=0:
    #             result = fun(**params)
    #         else:
    #             result = fun(locator, **params)
    #         return result

    def click_by_img(self, handler,img_name,img_path):
        """
        点击图片
        :param img_path:
        :return:
        """
        handler.set_step_des("点击图片：" + img_name)
        handler.set_detail("图片路径：" + img_path)
        img_path = self.download_img(img_path)

    def app_start(self,package_name):
        logger.info("Start app: %s" % package_name)
        self.deviceV2.app_start(package_name,wait=True)

    def app_close(self,package_name):
        logger.info("Close app: %s" % package_name)
        self.deviceV2.app_stop(package_name)

    def get_device_info(self,driver):
        """
        获取设备信息
        :param device:
        :return:
        """
        logger.debug(
            f"Phone Name: {driver.get_info()['productName']}, SDK Version: {driver.get_info()['sdkInt']}"
        )
        if int(driver.get_info()["sdkInt"]) < 19:
            logger.warning("Only Android 4.4+ (SDK 19+) devices are supported!")
        logger.debug(
            f"Screen dimension: {driver.get_info()['displayWidth']}x{driver.get_info()['displayHeight']}"
        )
        logger.debug(
            f"Screen resolution: {driver.get_info()['displaySizeDpX']}x{driver.get_info()['displaySizeDpY']}"
        )
        logger.debug("device_info: %s" % driver.deviceV2.device_info)

    def _get_current_app(self):
        """
        获取当前app的包名
        :return:
        """
        try:
            return self.deviceV2.app_current()["package"]
        except uiautomator2.JSONRPCError as e:
            raise DeviceFacade.JsonRpcError(e)
    def _is_opened(self) -> bool:
        """
        打开的是否为当前的app
        :return:
        """
        return self._get_current_app() == self.app_id
    def check_is_opened(func):
        """
        检查是否打开了指定的app
        :return:
        """
        def wrapper(self, **kwargs):
            avoid_lst = ["choose_cloned_app", "check_if_crash_popup_is_there"]
            caller = stack()[1].function
            if not self._is_opened() and caller not in avoid_lst:
                raise DeviceFacade.AppHasCrashed("App has crashed / has been closed!")
            return func(self, **kwargs)

        return wrapper


    def assert_equal(self, expect, actual):
        """
        断言预期值与实际值是否相等
        :param expect: 预期值
        :param actual: 实际值
        """
        assert expect == actual, "预期值为：{}，实际值为：{},断言失败!".format(expect, actual)



    def assert_exited(self, element):
        '''
        断言当前页面存在要查找的元素,存在则判断成功
        :param driver:
        :return:
        '''
        assert self.k_find_elements(element, timeout=10) is True, "断言{}元素是否存在,失败!".format(element)
        logger.info("断言{}元素存在,成功!".format(element))



    # 返回view 对象
    def find(
        self,
        index=None,
        **kwargs,
    ):
        try:
            logger.info("find element: %s" % kwargs)
            selector=None
            value=None
            new_kwargs = {}
            view = None
            if "selector" in kwargs:
                # 取出kwargs中的selector
                selector = kwargs.get("selector")
                logger.info("selector:::::::: %s" % selector)
            if "value" in kwargs:
                value = kwargs.get("value")
                logger.info("value:::::::: %s" % value)
            # 循环遍历出kwargs中的所有key 对应的value
            if selector is not None and value is not None:
                new_kwargs[selector] = value
                logger.info("new_kwargs:::::::: %s" % new_kwargs)
                # 支持的元素定位参考Selector类的属性
                # 判断下kwargs的key是否在Selector中存在，如果不存在，则抛出异常
                # 遍历 new_kwargs
                for key,value in new_kwargs.items():
                    logger.info("key:{0},value:{1}".format(key,value))
                    kws= getattr(Selector,"_Selector__fields")
                    logger.info("kws----------------->{}".format(kws))
                    if key not in getattr(Selector,"_Selector__fields"):
                       logger.error("查找元素失败，没有这个：{}元素类型！".format(key))
                       raise AttributeError("查找元素失败，没有这个{}元素类型！".format(key))
                    view = self.deviceV2(**new_kwargs)
                    if index is not None and view.count > 1:
                        view = self.deviceV2(**new_kwargs)[index]
            else:
                view = self.deviceV2(**kwargs)
                # if index is not None and view.count > 1:
                #     view = self.deviceV2(**kwargs)[index]
        except uiautomator2.JSONRPCError as e:
            raise DeviceFacade.JsonRpcError(e)
        return DeviceFacade.View(view=view, device=self.deviceV2)



    def click_wait(self, timeout=10, **kwargs):
        """
        当timeout s内对象出现就点击
        :param timeout: 超时时间
        :param kwargs: 元素定位
        :return:
        """
        self.find1(**kwargs).click_exists(timeout)

    def get_toast(self, wait_timeout=15,
                  cache_timeout=8,
                  default=None):
        """
        获取toast提示
        :param wait_timeout: 超时时间
        :param cache_timeout: 从现在开始多少时间以内
        :param default: 超时提示
        :return:
        """
        toast = self.viewV2.toast.get_message(wait_timeout=wait_timeout,
                                              cache_timeout=cache_timeout,
                                              default=default)
        if toast:
            self.reset_toast()
        return toast

    def reset_toast(self):
        """
        清除设备toast提示
        :return:
        """
        self.viewV2.toast.reset()

    def k_find_elements(self, locator, timeout=None):
        '''
        查找元素是否存在当前页面
        :return:
        '''
        is_exited = False
        try:
            while timeout > 0:
                xml = self.deviceV2.dump_hierarchy()
                for key,value in locator.items():
                    if re.findall(value, xml):
                        is_exited = True
                        logger.info("查询到元素：[{}]".format(value))
                        return is_exited
                    else:
                        logger.info("未查询到元素.............：[{}]".format(value))
                        timeout -= 1
                        time.sleep(1)
            return is_exited
        except Exception as e:
            logger.error("{}查找失败!{}".format(locator, e))



    def loop_watcher(self,view=None, timeout=10):
        """
        循环查找函数：每隔一秒，循环查找元素是否存在. 如果元素存在，click操作
        :param find_element: 要查找元素，需要是poco对象
        :param timeout: 超时时间，单位：秒
        :return:
        """
        # view : UiObject ,XPathSelector
        # 判断xPathSelector对象是否存在
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

    def find_element_view(
        self,
        index=None,
        timeout=10,
        **kwargs,
    ):
        logger.info("find element: %s" % kwargs)
        # 支持的元素定位参考Selector类的属性
        # 判断下kwargs的key是否在Selector中存在，如果不存在，则抛出异常
        # 遍历 new_kwargs
        view = None
        try:
            if kwargs is not None:
                for key,value in kwargs.items():
                    if "xpath" in key:
                        view = self.find_by_xpath(value)
                    else:
                        # kws= getattr(Selector,"_Selector__fields")
                        # logger.info("kws----------------->{}".format(kws))
                        if key not in getattr(Selector,"_Selector__fields"):
                           logger.error("查找元素失败，没有这个：{}元素类型！".format(key))
                           # raise AttributeError("查找元素失败，没有这个{}元素类型！".format(key))
                        view = self.deviceV2(**kwargs)
                        if index is not None and view.count > 1:
                            view = self.deviceV2(**kwargs)[index]
            if self.loop_watcher(view, timeout):
                return DeviceFacade.View(view=view, device=self.deviceV2)
            else:
                return None
        except Exception as e:
            logger.error("查找元素失败，没有这个：{}元素类型！，异常：{}".format(kwargs,e))
            raise  AttributeError("查找元素失败，没有这个{}元素类型！".format(kwargs))

    def find_view(self,locator,index=None,timeout=10):
        logger.info("find element: %s" % locator)
        # 支持的元素定位参考Selector类的属性
        # 判断下kwargs的key是否在Selector中存在，如果不存在，则抛出异常
        # 遍历 new_kwargs
        view = None
        try:
            if locator is not None:
                for key, value in locator.items():
                    logger.info("key:{0},value:{1}".format(key, value))
                    if "xpath" in key:
                        logger.info("xpath:::::::: %s" % value)
                        view = self.find_by_xpath(value)
                    else:
                        kws = getattr(Selector, "_Selector__fields")
                        logger.info("kws----------------->{}".format(kws))
                        if key not in getattr(Selector, "_Selector__fields"):
                            logger.error("查找元素失败，没有这个：{}元素类型！".format(key))
                            raise AttributeError("查找元素失败，没有这个{}元素类型！".format(key))
                        view = self.deviceV2(**locator)
                        if index is not None and view.count > 1:
                            view = self.deviceV2(**locator)[index]
            if self.loop_watcher(view, timeout):
                return DeviceFacade.View(view=view, device=self.deviceV2)
            else:
                return None
        except Exception as e:
            logger.error("查找元素失败，没有这个：{}元素类型！，异常：{}".format(locator, e))
            raise AttributeError("查找元素失败，没有这个{}元素类型！".format(locator))



    def find_element(self,locator, timeout=10):
        """
        查找元素是否存在当前页面
        :return:
        """
        is_exited = False
        try:
            while timeout > 0:
                xml = self.deviceV2.dump_hierarchy()
                for key,value in locator.items():
                    if re.findall(value, xml):
                        is_exited = True
                        logger.info("查询到元素：[{}]".format(value))
                        return is_exited
                    else:
                        logger.info("未查询到元素.............：[{}]".format(value))
                        timeout -= 1
                        time.sleep(1)
            return is_exited
        except Exception as e:
            logger.error("{}查找失败!{}".format(locator, e))


    def find_by_xpath(self, xpath):
        """
        通过xpath查找元素
        :param xpath:
        :return:
        """
        try:
            return self.deviceV2.xpath(xpath)
        except uiautomator2.JSONRPCError as e:
            raise DeviceFacade.JsonRpcError(e)



    def back(self):
        logger.debug("Press back button.")
        self.deviceV2.press("back")
        random_sleep()

    def start_screenrecord(self, output="debug_0000.mp4", fps=20):
        import imageio

        def _run_MOD(self):
            from collections import deque

            pipelines = [self._pipe_limit, self._pipe_convert, self._pipe_resize]
            _iter = self._iter_minicap()
            for p in pipelines:
                _iter = p(_iter)

            with imageio.get_writer(self._filename, fps=self._fps) as wr:
                frames = deque(maxlen=self._fps * 30)
                for im in _iter:
                    frames.append(im)
                if self.crash:
                    for frame in frames:
                        wr.append_data(frame)
            self._done_event.set()

        def stop_MOD(self, crash=True):
            """
            stop record and finish write video
            Returns:
                bool: whether video is recorded.
            """
            if self._running:
                self.crash = crash
                self._stop_event.set()
                ret = self._done_event.wait(10.0)

                # reset
                self._stop_event.clear()
                self._done_event.clear()
                self._running = False
                return ret

        from uiautomator2 import screenrecord as _sr

        _sr.Screenrecord._run = _run_MOD
        _sr.Screenrecord.stop = stop_MOD
        mp4_files = [f for f in listdir(getcwd()) if f.endswith(".mp4")]
        if mp4_files:
            last_mp4 = mp4_files[-1]
            debug_number = "{0:0=4d}".format(int(last_mp4[-8:-4]) + 1)
            output = f"debug_{debug_number}.mp4"
        self.deviceV2.screenrecord(output, fps)
        logger.warning("Screen recording has been started.")

    def stop_screenrecord(self, crash=True):
        if self.deviceV2.screenrecord.stop(crash=crash):
            logger.warning("Screen recorder has been stopped successfully!")

    def screenshot(self, path):
        self.deviceV2.screenshot(path)

    def dump_hierarchy(self, path):
        xml_dump = self.deviceV2.dump_hierarchy()
        with open(path, "w", encoding="utf-8") as outfile:
            outfile.write(xml_dump)

    def press_power(self):
        self.deviceV2.press("power")
        sleep(2)

    def is_screen_locked(self):
        data = run(
            f"adb -s {self.deviceV2.serial} shell dumpsys window",
            encoding="utf-8",
            stdout=PIPE,
            stderr=PIPE,
            shell=True,
        )
        if data != "":
            flag = search("mDreamingLockscreen=(true|false)", data.stdout)
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
            flag = search("mInputShown=(true|false)", data.stdout)
            return flag.group(1) == "true"
        else:
            logger.debug(
                f"'adb -s {self.deviceV2.serial} shell dumpsys input_method' returns nothing!"
            )
            return None

    def is_alive(self):
        try:
            return self.deviceV2._is_alive()  # deprecated method
        except AttributeError:
            return self.deviceV2.server.alive

    def wake_up(self):
        """Make sure core is alive or bring it back up before starting."""
        if self.deviceV2 is not None:
            attempts = 0
            while not self.is_alive() and attempts < 5:
                self.get_info()
                attempts += 1

    def unlock(self):
        self.swipe(Direction.UP, 0.8)
        sleep(2)
        logger.debug(f"Screen locked: {self.is_screen_locked()}")
        if self.is_screen_locked():
            self.swipe(Direction.RIGHT, 0.8)
            sleep(2)
            logger.debug(f"Screen locked: {self.is_screen_locked()}")

    # 关闭屏幕
    def screen_off(self):
        self.deviceV2.screen_off()

    def get_orientation(self):
        try:
            return self.deviceV2._get_orientation()
        except uiautomator2.JSONRPCError as e:
            raise DeviceFacade.JsonRpcError(e)

    def window_size(self):
        """return (width, height)"""
        try:
            self.deviceV2.window_size()
        except uiautomator2.JSONRPCError as e:
            raise DeviceFacade.JsonRpcError(e)

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
            DeviceFacade.sleep_mode(SleepTime.TINY)
        except uiautomator2.JSONRPCError as e:
            raise DeviceFacade.JsonRpcError(e)

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
            DeviceFacade.sleep_mode(SleepTime.TINY)
        except uiautomator2.JSONRPCError as e:
            raise DeviceFacade.JsonRpcError(e)

    def get_info(self):
        # {'currentPackageName': 'net.oneplus.launcher', 'displayHeight': 1920, 'displayRotation': 0, 'displaySizeDpX': 411,
        # 'displaySizeDpY': 731, 'displayWidth': 1080, 'productName': 'OnePlus5', '
        #  screenOn': True, 'sdkInt': 27, 'naturalOrientation': True}
        try:
            return self.deviceV2.info
        except uiautomator2.JSONRPCError as e:
            raise DeviceFacade.JsonRpcError(e)

    def get_ip(self):
        try:
            return self.deviceV2.wlan_ip
        except uiautomator2.JSONRPCError as e:
            raise DeviceFacade.JsonRpcError(e)

    @staticmethod
    def sleep_mode(mode):
        mode = SleepTime.DEFAULT if mode is None else mode
        if mode == SleepTime.DEFAULT:
            random_sleep()
        elif mode == SleepTime.TINY:
            random_sleep(0, 1)
        elif mode == SleepTime.SHORT:
            random_sleep(1, 2)
        elif mode == SleepTime.ZERO:
            pass
            # 打开app

    def open_app(self, package_name):
        self.deviceV2.app_start(package_name)



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
                    DeviceFacade.View(view=item, device=self.deviceV2)
                    for item in self.viewV2
                )
                return iter(children)
            except uiautomator2.JSONRPCError as e:
                raise DeviceFacade.JsonRpcError(e)

        # 通过反射获取关键字函数
        def get_kw_method(self, key):
            f = getattr(self, f"{key}", None)
            if not f:
                raise AttributeError(f"不存在的关键字: {key}")
            return f

        def ui_info(self):
            try:
                return self.viewV2.info
            except uiautomator2.JSONRPCError as e:
                raise DeviceFacade.JsonRpcError(e)

        def content_desc(self):
            try:
                return self.viewV2.info["contentDescription"]
            except uiautomator2.JSONRPCError as e:
                raise DeviceFacade.JsonRpcError(e)
        # 子元素定位
        def child(self, *args, **kwargs):
            try:
                logger.debug(f"Child: {args}, {kwargs}")
                view = self.viewV2.child(*args, **kwargs)
            except uiautomator2.JSONRPCError as e:
                raise DeviceFacade.JsonRpcError(e)
            return DeviceFacade.View(view=view, device=self.deviceV2)
        # 兄弟元素定位
        def sibling(self, *args, **kwargs):
            try:
                view = self.viewV2.sibling(*args, **kwargs)
            except uiautomator2.JSONRPCError as e:
                raise DeviceFacade.JsonRpcError(e)
            return DeviceFacade.View(view=view, device=self.deviceV2)
        # 某个元素的左边相对定位
        def left(self, *args, **kwargs):
            try:
                view = self.viewV2.left(*args, **kwargs)
            except uiautomator2.JSONRPCError as e:
                raise DeviceFacade.JsonRpcError(e)
            return DeviceFacade.View(view=view, device=self.deviceV2)

        # 某个元素的右边相对定位
        def right(self, *args, **kwargs):
            try:
                view = self.viewV2.right(*args, **kwargs)
            except uiautomator2.JSONRPCError as e:
                raise DeviceFacade.JsonRpcError(e)
            return DeviceFacade.View(view=view, device=self.deviceV2)

        def up(self, *args, **kwargs):
            try:
                view = self.viewV2.up(*args, **kwargs)
            except uiautomator2.JSONRPCError as e:
                raise DeviceFacade.JsonRpcError(e)
            return DeviceFacade.View(view=view, device=self.deviceV2)

        def down(self, *args, **kwargs):
            try:
                view = self.viewV2.down(*args, **kwargs)
            except uiautomator2.JSONRPCError as e:
                raise DeviceFacade.JsonRpcError(e)
            return DeviceFacade.View(view=view, device=self.deviceV2)

        def gesture(self, a, b, c, d, a1, b1, c1, d1, steps=100):
            """
            双指从(a,b)，(c,d)滑动(a1,b1)，(c1,d1)，步长100
            :param a:
            :param b:
            :param c:
            :param d:
            :param a1:
            :param b1:
            :param c1:
            :param d1:
            :param steps:
            :return:
            """
            self.viewV2.gesture((a, b), (c, d), (a1, b1), (c1, d1), steps=steps)

        def drag(self, sx, sy, ex, ey, steps=10):
            """
            从sx，sy坐标拖动至ex，ey坐标
            :param sx: 起点横坐标
            :param sy: 起点纵坐标
            :param ex: 终点横坐标
            :param ey: 终点纵坐标
            :param steps: 步长
            :return:
            """
            self.viewV2.drag(sx, sy, ex, ey, steps=steps)

        def get_screenshot_as_base64(self):
            """
            截屏并转换成base64
            :return:
            """
            content = self.viewV2.screenshot(format="raw")
            base64_data = base64.b64encode(content)
            return str(base64_data, "utf-8")

        def disable_popups(self, disable=True):
            """弹出窗口
            @:param disable True:自动跳过弹出窗口，False:禁用自动跳过弹出窗口
            """
            self.viewV2.disable_popups(disable)




        def click_exists(self, timeout=10):
            """
            点击存在的元素
            """
            try:
                return self.viewV2.click_exists(timeout)
            except uiautomator2.JSONRPCError as e:
                raise DeviceFacade.JsonRpcError(e)

        def click_gone(self, maxretry=3, interval=1.0):
            try:
                self.viewV2.click_gone(maxretry, interval)
            except uiautomator2.JSONRPCError as e:
                raise DeviceFacade.JsonRpcError(e)

        def click(self, mode=None, sleep=None, coord=None, crash_report_if_fails=True):
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
                    DeviceFacade.sleep_mode(sleep)
                    return
                except uiautomator2.JSONRPCError as e:
                    if crash_report_if_fails:
                        raise DeviceFacade.JsonRpcError(e)
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
                self.viewV2.click(
                    self.get_ui_timeout(Timeout.LONG),
                    offset=(x_offset, y_offset),
                )
                DeviceFacade.sleep_mode(sleep)

            except uiautomator2.JSONRPCError as e:
                if crash_report_if_fails:
                    raise DeviceFacade.JsonRpcError(e)
                else:
                    logger.debug("试图点击一个已经消失的对象.")
                raise Exception('点击失败')

        def click_retry(self, mode=None, sleep=None, coord=None, maxretry=2):
            """return True if successfully open the element, else False"""
            if coord is None:
                coord = []
            self.click(mode, sleep, coord)

            while maxretry > 0:
                # we wait a little more before try again
                random_sleep(2, 4, modulable=False)
                if not self.exists():
                    return True
                logger.debug("UI element didn't open! Try again..")
                self.click(mode, sleep, coord)
                maxretry -= 1
            if not self.exists():
                return True
            logger.warning("Failed to open the UI element!")
            return False

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
                    f"Double click in ({random_x},{random_y}) with t={int(time_between_clicks*1000)}ms. Surface: ({visible_bounds['left']}-{visible_bounds['right']},{visible_bounds['top']}-{visible_bounds['bottom']})."
                )
                self.deviceV2.double_click(
                    random_x, random_y, duration=time_between_clicks
                )
                DeviceFacade.sleep_mode(SleepTime.DEFAULT)
            except uiautomator2.JSONRPCError as e:
                raise DeviceFacade.JsonRpcError(e)

        def scroll(self, direction):
            try:
                if direction == Direction.UP:
                    self.viewV2.scroll.toBeginning(max_swipes=1)
                else:
                    self.viewV2.scroll.toEnd(max_swipes=1)
            except uiautomator2.JSONRPCError as e:
                raise DeviceFacade.JsonRpcError(e)

        def scroll_up_to_content_element(self, max_scroll_num=15, **kwargs):
            """
            向上滑动直到某个元素出现
            :param max_scroll_num: 最大滑动次数
            :param kwargs: 元素定位
            :return:
            """
            DeviceFacade.sleep_mode(SleepTime.DEFAULT)
            num = 0
            while num < max_scroll_num:
                if self.exists(timeout=0.5, **kwargs):
                    return True
                else:
                    try:
                        self.swipe_up_screen(0.5, steps=20)
                    except:
                        return False
                num = num + 1
                self.sleep(0.2)
            if num == max_scroll_num:
                return False
            else:
                return True

        def vert_backward_to_content_element(self, **kwargs):
            """
            向下滑动直到某个元素出现
            :param kwargs: 元素定位
            :return:
            """
            while True:
                if self.exists(**kwargs):
                    break
                else:
                    self.viewV2(scrollable=True).scroll.vert.backward(steps=100)



        def fling(self, direction):
            try:
                if direction == Direction.UP:
                    self.viewV2.fling.toBeginning(max_swipes=5)
                else:
                    self.viewV2.fling.toEnd(max_swipes=5)
            except uiautomator2.JSONRPCError as e:
                raise DeviceFacade.JsonRpcError(e)

        def exists(self, ui_timeout=None, ignore_bug: bool = False) -> bool:
            logger.debug(f"Checking if {self} exists")
            """
            检查一个视图是否存在
            :param ui_timeout: 超时时间
            :param ignore_bug: 忽略bug
            """
            try:
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
                raise DeviceFacade.JsonRpcError(e)

        def count_items(self) -> int:
            try:
                return self.viewV2.count
            except uiautomator2.JSONRPCError as e:
                raise DeviceFacade.JsonRpcError(e)

        def wait(self, timeout):
            """
            等待一个元素出现
            :param timeout: 超时时间
            :param interval: 间隔时间
            """
            try:
                return self.viewV2.wait(timeout=timeout)
            except uiautomator2.JSONRPCError as e:
                raise DeviceFacade.JsonRpcError(e)

        def wait_gone(self, ui_timeout=None):
            """
            等待一个元素消失
            """
            try:
                return self.viewV2.wait_gone(timeout=self.get_ui_timeout(ui_timeout))
            except uiautomator2.JSONRPCError as e:
                raise DeviceFacade.JsonRpcError(e)

        def is_above_this(self, obj2) -> Optional[bool]:
            obj1 = self.viewV2
            obj2 = obj2.viewV2
            try:
                if obj1.exists() and obj2.exists():
                    return obj1.info["bounds"]["top"] < obj2.info["bounds"]["top"]
                else:
                    return None
            except uiautomator2.JSONRPCError as e:
                raise DeviceFacade.JsonRpcError(e)

        def get_bounds(self) -> dict:
            try:
                return self.viewV2.info["bounds"]
            except uiautomator2.JSONRPCError as e:
                raise DeviceFacade.JsonRpcError(e)

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
                raise DeviceFacade.JsonRpcError(e)

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
                    raise DeviceFacade.JsonRpcError(e)
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
                raise DeviceFacade.JsonRpcError(e)

        def register_watcher_click(self, name, **kwargs):
            """
            创建并运行监听器
            :param name:
            :param kwargs:
            :return:
            """
            watcher = self.viewV2.watcher(name).when(**kwargs).click(**kwargs)
            self.watchers_run()
            return watcher

        def remove_watcher(self, name):
            """
            移除监听器
            :param name: 监听器名字
            :return:
            """
            self.viewV2.watcher(name).remove()

        def watchers(self):
            """
            获取所有监听器
            :return:
            """
            return self.viewV2.watcher()

        def watchers_triggered(self, name):
            """
            获取所有已触发监听器
            :param name:
            :return:
            """
            return self.viewV2.watcher(name).triggered

        def watchers_reset(self):
            """
            重置所有已触发的监视器
            :return:
            """
            self.viewV2.watchers.reset()

        def watchers_run(self):
            """
            运行所有已注册的监听器
            :return:
            """
            self.viewV2.watchers.run()



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
                    random_sleep(0.3, 1, modulable=False)
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
                            f"Text typed in: {(datetime.now()-start).total_seconds():.2f}s"
                        )
                DeviceFacade.sleep_mode(SleepTime.SHORT)
            except uiautomator2.JSONRPCError as e:
                raise DeviceFacade.JsonRpcError(e)

    class JsonRpcError(Exception):
        pass

    class AppHasCrashed(Exception):
        pass

    def download_img(self, img_file):
        """
        下载图片
        :param img_path:
        :return:
        """
        logger.info("正在下载图片{}".format(img_file))
        try:
            url = img_file
            response = requests.get(url)
            # 获取的文本实际上是图片的二进制文本
            img = response.content
            # 保存路径
            img_path = self.config["download"]["download_path"]+img_file
            with open(img_path, 'wb') as f:
                f.write(img)
            return f
        except Exception as ex:
            logger.error("出错了{}".format(ex))


if __name__ == '__main__':
    driver = create_device('17095c46',"com.hollyland.cameralive")

