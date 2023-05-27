from pip import main
from window_terminal import WindowTerminal
import subprocess

def callback():
    print()
if __name__ == '__main__':
    window = WindowTerminal.create_window()
    window.open()
    window.input("adb device",callback)
    window.wait_close()


    # subprocess.Popen("", shell=True, stdout=subprocess.PIPE)