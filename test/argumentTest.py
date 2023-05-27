import argparse
import sys


# python .\argumentTest.py -n false -f asdasd,bbb -d 111,222 -r 123.txt
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="test")
    parser.add_argument("-n", required=False, type=str, default="false", help="True为None-GUI")
    parser.add_argument("-f", required=False, type=list, default=[], help="传入的用例文件")
    parser.add_argument("-d", required=False, type=list, default=[], help="被测设备")
    parser.add_argument("-r", required=False, type=str, default=sys.path, help="测试报告地址")
    args = parser.parse_args()

    print(args.f)
    print(args.n)
    print(args.d)
    print(args.r)


