import os

from PyQt5.QtCore import QThread


class TestQThread(QThread):

    def run(self):
        print("Testing Thread！！！")


if __name__ == '__main__':
    s = ['boot_images']
    os.environ.setdefault("WORKSPACE", os.path.abspath(os.path.dirname(os.path.realpath(__file__))))
    workspace = os.environ["WORKSPACE"]
    print(f"{workspace}")
    if 'broadcast.py' in os.environ["WORKSPACE"]:
        print("ok")

    filelist = os.listdir(workspace)
    for file in filelist:
        print(f"{file}")
