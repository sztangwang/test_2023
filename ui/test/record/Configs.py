from win32 import win32api, win32gui, win32print
from win32.lib import win32con

screen_width = win32print.GetDeviceCaps(win32gui.GetDC(0), win32con.DESKTOPHORZRES) # 电脑屏幕宽
   

revolve = 0                     # 旋转屏幕角度

is_image_show = False            # 图像预览显示

IMAGE_SHOW_BUTTON = None        # 图像预览button 状态

run_button = '运行'             # 运行按钮字符

device_dict = {}                # 设备列表

adb_devices = None

ac_port = ''                    # Ac按钮字符

select_script_file = ''         #脚本文件

selection_line_run_rows = None  # 选择指定行运行


is_screenshot = ''              # 是否截图

screenshot_file = ''            # 截图文件目录

