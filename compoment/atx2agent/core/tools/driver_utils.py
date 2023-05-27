import os
import re
import shutil
import subprocess
import sys
import time
from datetime import datetime
from random import randint, shuffle, uniform
from subprocess import PIPE
from time import sleep
from typing import Optional, Tuple, Union
from urllib.parse import urlparse
import adbutils
import emoji
import pytest
from apkutils2.axml.public import resources
from colorama import Style, Fore

from compoment.atx2agent.core.common.logs.log_uru import Logger

logger = Logger().get_logger



@pytest.fixture(scope="session", autouse=True)
def load_config(config_yaml):
    config=config_yaml
    global app_id
    global ResourceID
    global configs
    configs=config
    app_id = configs.get_node_key_value("env.test.app_info","app_package")
    ResourceID = resources(app_id)

@pytest.fixture(scope="session", autouse=True)
def check_adb_connection(config_yaml):
    """
    Check if adb is connected to the device
    """
    configs = config_yaml
    # 读取设备信息的设备id
    device_id = configs.get_node_key_value("env.test.device_info","device_id")
    logger.info("Checking adb connection...")
    is_device_id_provided = device_id is not None
    stream = os.popen("adb devices")
    stream.close()
    stream = os.popen("adb devices")
    output = stream.read()
    devices_count = len(re.findall("device\n", output))
    stream.close()

    is_ok = True
    message = "That's ok."
    if devices_count == 0:
        is_ok = False
        message = "Cannot proceed."
    elif devices_count > 1 and not is_device_id_provided:
        is_ok = False
        message = "Set a device name in your config.yml"
    if is_ok:
        logger.debug(f"Connected devices via adb: {devices_count}. {message}")
    else:
        logger.error(f"Connected devices via adb: {devices_count}. {message}")
    return is_ok

# 获取应用的版本号
def get_app_version():
    stream = os.popen(
        f"adb{'' if configs.device_id is None else ' -s ' + configs.device_id} shell dumpsys package {app_id}"
    )
    output = stream.read()
    version_match = re.findall("versionName=(\\S+)", output)
    version = version_match[0] if len(version_match) == 1 else "not found"
    stream.close()
    return version

#  停止APP 应用程序
def kill_app(device, app_id):
    device.deviceV2.app_stop(app_id)



def get_adb_devices():
   # 通过adb utils 获取设备列表
    devices = adbutils.adb.device_list()
    return devices

# 通知开启/关闭
def head_up_notifications(enabled: bool = False):
    """
    Enable or disable head-up-notifications
    """
    cmd: str = f"adb{'' if configs.device_id is None else ' -s ' + configs.device_id} shell settings put global heads_up_notifications_enabled {0 if not enabled else 1}"
    return subprocess.run(cmd, stdout=PIPE, stderr=PIPE, shell=True, encoding="utf8")

# 检查屏幕超时时间
def check_screen_timeout():
    MIN_TIMEOUT = 5 * 6_000
    cmd: str = f"adb{'' if configs.device_id is None else ' -s ' + configs.device_id} shell settings get system screen_off_timeout"
    resp = subprocess.run(cmd, stdout=PIPE, stderr=PIPE, shell=True, encoding="utf8")
    if int(resp.stdout.lstrip()) < MIN_TIMEOUT:
        logger.info(
            f"Setting timeout of the screen to {MIN_TIMEOUT/6_000:.0f} minutes."
        )
        cmd: str = f"adb{'' if configs.device_id is None else ' -s ' + configs.device_id} shell settings put system screen_off_timeout {MIN_TIMEOUT}"
        subprocess.run(cmd, stdout=PIPE, stderr=PIPE, shell=True, encoding="utf8")
    else:
        logger.info("Screen timeout is fine!")

def open_app(device):
    # TODO 从配置文件中读取数据，打开app 的时候是否开启录制视频，是否开启logcat记录
    nl = "\n"
    logger.info("打开Camera应用!!!")
    # 启动应用
    def call_camera():
        cmd ="am start -n com.hollyland.cameralive/.ui.CameraLiveMainActivity"
        output = device.deviceV2.shell(cmd)
        logger.info(output)
        return output
    err = call_camera()
    if "Error" in err:
        logger.error(err.replace(nl, ". "))
        return False
    elif "more than one device/emulator" in err:
        logger.error(
            f"{err[9:].capitalize()}, 在 config.yml 文件的`device: devicename` 只能指定一个设备。"
        )
        return False
    elif err == "":
        logger.debug("camera 启动成功！")
    else:
        logger.debug(f"{err.replace('Warning: ', '')}.")
    logger.info("准备就绪了!🤫", extra={"color": f"{Style.BRIGHT}{Fore.GREEN}"})
    return True

# 关闭camera应用  # todo
def close_camera(device):
    logger.info("关闭 Camera app.")
    device.deviceV2.app_stop(app_id)
    random_sleep(5, 5, modulable=False)
    if configs.screen_record:
        try:
            # 停止录制视频
            device.stop_screenrecord(crash=False)
        except Exception as e:
            logger.error(
                f"如果不安装依赖项，您将无法使用此功能。 在控制台输入: 'pip3 install -U \"uiautomator2[image]\" -i https://pypi.doubanio.com/simple'. 异常: {e}"
            )

# 检查是否有奔溃弹出框  # todo
def check_if_crash_popup_is_there(device) -> bool:
    obj = device.find(resourceId=ResourceID.CRASH_POPUP)
    if obj.exists():
        obj.click()
        return True
    return False



# 等待消息出现的时间  # todo
def countdown(seconds: int = 10, waiting_message: str = "") -> None:
    while seconds:
        print(waiting_message, f"{seconds:02d}", end="\r")
        time.sleep(1)
        seconds -= 1


# 前置/后置脚本  # todo
def pre_post_script(path: str, pre: bool = True):
    if path is not None:
        if os.path.isfile(path):
            logger.info(f"运行 '{path}' as {'pre' if pre else 'post'} script.")
            try:
                p1 = subprocess.Popen(path)
                p1.wait()
            except Exception as ex:
                logger.error(f"发生了异常: {ex}")
        else:
            logger.error(
                f"文件 '{path}' 不存在. 请检查拼写是否正确 (相对路径是这样的: '{os.getcwd()}')."
            )



# 产生一个随机的等待时间
def random_sleep(inf=0.5, sup=1.0, modulable=True, log=True):
    MIN_INF = 0.3
    # multiplier = float(configs.get("app").get("speed_multiplier"))
    delay = uniform(inf, sup) / 1.0
    delay = max(delay, MIN_INF)
    if log:
        logger.debug(f"{str(delay)[:4]}s sleep")
    sleep(delay)




def trim_txt(source: str, target: str) -> None:
    with open(source, "r", encoding="utf-8") as f:
        lines = f.readlines()
    tail = next(
        (
            index
            for index, line in enumerate(lines[::-1])
            if line.find("Arguments used:") != -1
        ),
        250,
    )
    rem = lines[-tail:]
    with open(target, "w", encoding="utf-8") as f:
        f.writelines(rem)

# 停止atx-core
def kill_atx_agent(driver,device):
    """
    1. 恢复默认键盘
    2. 关闭atx-core
    :param device:
    :return:
    """
    # _restore_keyboard(driver)
    logger.info("Kill atx core.")
    device.shell("pkill atx-core")

# 恢复默认键盘
# def _restore_keyboard(driver):
#     logger.debug("Back to default keyboard!")
#     driver.set_fastinput_ime(False)

def stop_app(driver,device,  was_sleeping=False):
    close_camera(device)
    kill_atx_agent(driver,device)
    head_up_notifications(enabled=True)
    logger.info(
        f"-------- FINISH: {datetime.now().strftime('%H:%M:%S')} --------",
        extra={"color": f"{Style.BRIGHT}{Fore.YELLOW}"},
    )
    sys.exit(2)


def can_repeat(current_session, max_sessions: int) -> bool:
    if max_sessions == -1:
        return True
    logger.info(
        f"You completed {current_session} session(s). {max_sessions-current_session} session(s) left.",
        extra={"color": f"{Style.BRIGHT}{Fore.YELLOW}"},
    )
    if current_session < max_sessions:
        return True
    logger.info(
        "You reached the total-sessions limit! Finish.",
        extra={"color": f"{Style.BRIGHT}{Fore.YELLOW}"},
    )
    return False


def get_value(
    count: str,
    name: Optional[str],
    default: Union[int, float] = 0,
    its_time: bool = False,
) -> Optional[Union[int, float]]:
    def print_error() -> None:
        logger.error(
            f'Using default value instead of "{count}", because it must be '
            "either a number (e.g. 2) or a range (e.g. 2-4)."
        )

    if count is None:
        return None
    parts = count.split("-")
    try:
        if len(parts) == 1:
            if "." in count:
                value = float(count)
            else:
                value = int(count)
        elif len(parts) == 2:
            if not its_time:
                value = randint(int(parts[0]), int(parts[1]))
            else:
                value = round(uniform(int(parts[0]), int(parts[1])), 2)
        else:
            raise ValueError
    except ValueError:
        value = default
        print_error()
    if name is not None:
        logger.info(name.format(value), extra={"color": Style.BRIGHT})
    return value


def validate_url(x) -> bool:
    try:
        result = urlparse(x)
        return all([result.scheme, result.netloc, result.path])
    except Exception as e:
        logger.error(f"Error validating URL {x}. Error: {e}")
        return False


def append_to_file(filename: str, username: str) -> None:
    try:
        if not filename.lower().endswith(".txt"):
            filename += ".txt"
        with open(filename, "a+", encoding="utf-8") as file:
            file.write(username + "\n")
    except Exception as e:
        logger.error(f"Failed to append {username} to: {filename}. Exception: {e}")


def sample_sources(sources, n_sources):
    from random import sample

    sources_limit_input = n_sources.split("-")
    if len(sources_limit_input) > 1:
        sources_limit = randint(
            int(sources_limit_input[0]), int(sources_limit_input[1])
        )
    else:
        sources_limit = int(sources_limit_input[0])
    if len(sources) < sources_limit:
        sources_limit = len(sources)
    if sources_limit == 0:
        truncaded = sources
        shuffle(truncaded)
    else:
        truncaded = sample(sources, sources_limit)
        logger.info(
            f"Source list truncated at {len(truncaded)} {'item' if len(truncaded)<=1 else 'items'}."
        )
    logger.info(
        f"In this session, {'that source' if len(truncaded)<=1 else 'these sources'} will be handled: {', '.join(emoji.emojize(str(x), use_aliases=True) for x in truncaded)}"
    )
    return truncaded


def random_choice(number: int) -> bool:
    """
    Generate a random int and compare with the argument passed
    :param int number: number passed
    :return: is argument greater or equal then a random generated number
    :rtype: bool
    """
    return number >= randint(1, 100)


def wait_for_next_session(time_left, driver, device):
    hours, remainder = divmod(time_left.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    kill_atx_agent(driver,device)
    logger.info(
        f'Next session will start at: {(datetime.now()+ time_left).strftime("%H:%M:%S (%Y/%m/%d)")}.',
        extra={"color": f"{Fore.GREEN}"},
    )
    logger.info(
        f"Time left: {hours:02d}:{minutes:02d}:{seconds:02d}.",
        extra={"color": f"{Fore.GREEN}"},
    )
    try:
        sleep(time_left.total_seconds())
    except KeyboardInterrupt:
        stop_app(driver,device, was_sleeping=True)



