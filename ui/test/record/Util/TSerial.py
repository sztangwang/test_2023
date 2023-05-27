# -*-coding:UTF-8-*- #
import re
import time
import serial
import threading
import serial.tools.list_ports
from ui.test.record.Util import TFile


_TIMEOUTS = 1
FLUKE = "Prolific USB-to-Serial Comm Port"
REMOTE = "USB-SERIAL CH340"
SERIAL = "USB Serial Port"
CHROMA = "Prolific USB-to-Serial Comm Port"

FUZZY_MATCH = 0
PRECISE_MATCH = 1


class SerialPort(object):
    def __init__(self, port, baud_rate=115200, description=SERIAL):
        try:
            self.filename = TFile.get_cache_file(r"Serial\Port_%s\%s.log" % (port, self._get_datetime("%Y%m%d")))
            self.serial_port = serial.Serial(port=port, baudrate=baud_rate)
            self.serial_port.timeout = _TIMEOUTS
    
        except Exception:
            raise

    @staticmethod
    def _get_serial_dict_ports():
        dict_ports = {}
        comports = list(serial.tools.list_ports.comports())
        for p in comports:
            # print(p.description)
            dict_ports[p.device] = p.description
        return dict_ports

    @staticmethod
    def _bytes_to_str(rec):
        data = rec.decode('utf-8', 'ignore')
        return data

    @staticmethod
    def _get_datetime(format_str="%Y/%m/%d%H_%M_%S"):
        return time.strftime(format_str, time.localtime())

    def _recording(self, data):
        with open(self.filename, 'a',encoding='utf-8') as fp:
            fp.write(data)
            fp.flush()

    def _record_at_thread(self, fp):
        while self._record:
            fp.write(self.read_all())
            fp.flush()
            time.sleep(0.2)
        fp.close()

    def _show_write(self, write_data):
        if re.search(r"\S+", write_data):
            data = "%s [_write_] %s" % (self._get_datetime(), write_data)
            print(re.sub(r"\r+|\n+", "", data))
            self._recording(data)

    def _show_receive(self, receive_data):
        if re.search(r"\S+", receive_data):
            for rec in re.findall(".*", receive_data):
                if re.search(r"\S+", rec):
                    data = "%s [receive] %s" % (self._get_datetime(), rec)
                    print(re.sub(r"\r+|\n+", "", data))
                    self._recording(data)

    def open(self):
        """
        Open SerialPort
        :return: bool
        """
        if self.serial_port.is_open:
            return True
        self.serial_port.open()
        return True

    def close(self):
        """
        Close SerialPort
        :return: bool
        """
        # if self.serial_port.is_open:
        #     self.serial_port.close()
        #     return True
        try:
            self.serial_port.close()
        except:
            pass
        return True

    def flush_input(self):
        self.serial_port.flushInput()

    def flush_output(self):
        self.serial_port.flushOutput()

    def write(self, data):
        """
        Write data
        :param data: str
        :return: None
        """
        data = "%s\n" % data
        self.serial_port.write(data.encode(encoding="GBK"))
        self._show_write(data)
        self.serial_port.flush()

    def write_for_hex(self, hex_str):
        self.serial_port.write(bytes.fromhex(hex_str))

    def interrupt(self):
        """
        Write Ctrl+C
        :return: None
        """
        self.serial_port.write(bytes.fromhex('03'))

    def read(self, size=1024):
        """
        Read data(size)
        :param size: int
        :return: str
        """
        rec = self.serial_port.read(size)
        data = self._bytes_to_str(rec)
        self._show_receive(data)
        return data

    def read_line(self):
        """
        Read data(a line)
        :return: str
        """
        rec = self.serial_port.readline()
        data = self._bytes_to_str(rec)
        self._show_receive(data)
        return data

    def read_lines(self):
        """
        Read data(any lines)
        :return: list
        """
        list_data = []
        read_lines = self.serial_port.readlines()
        for rec in read_lines:
            data = self._bytes_to_str(rec)
            self._show_receive(data)
            list_data.append(data)
        return list_data

    # 2015/5/18 新增读取串口数据，返回字符串
    def read_lines_(self):
        """
        Read data(any lines)
        :return: str
        """
        str_data = ''
        read_lines = self.serial_port.readlines()
        for rec in read_lines:
            data = self._bytes_to_str(rec)
            # self._show_receive(data)
            str_data += data
        return str_data

    def read_until(self, terminator, timeout=3):
        """
        Read data until found the terminator
        :param terminator: str
        :param timeout: int
        :return: str
        """
        try:
            self.serial_port.timeout = timeout
            rec = self.serial_port.read_until(terminator=terminator.encode(encoding="GBK"))
            data = self._bytes_to_str(rec)
            self._show_receive(data)
            return data
        finally:
            self.serial_port.timeout = _TIMEOUTS

    def read_all(self):
        """
        Read all
        :return: str
        """
        time.sleep(1)
        rec = self.serial_port.read_all()
        data = self._bytes_to_str(rec)
        self._show_receive(data)
        return data

    def read_with_time(self, timeout=3):
        """
        Read data(line by line) until timeout
        :param timeout: int
        :return: str
        """
        data = ""
        times = time.time()
        while time.time() - times < timeout:
            read_line = self.read_line()
            if read_line != "":
                data += read_line
        return data

    def read_with_time_list(self, timeout=3):
        """
        Read list_data(lines by lines) until timeout
        :param timeout: int
        :return: list
        """
        list_data = []
        times = time.time()
        while time.time() - times < timeout:
            read_lines = self.read_lines()
            list_data.extend(read_lines)
        return list_data

    def read_grep(self, keyword, timeout=2, match=PRECISE_MATCH):
        """
        Read data(line by line) grep keyword(first grep)
        :param keyword: str
        :param timeout: int
        :param match: constant
        :return: str
        """
        times = time.time()
        while time.time() - times < timeout:
            data = self.read_line()
            if match == PRECISE_MATCH and data != "" and keyword in data:
                return data
            elif match == FUZZY_MATCH and data != "" and keyword.upper() in data.upper():
                return data
        return ""

    def re_read_grep(self, pattern, timeout=5, ignore_case=False):
        """

        :param pattern: str
        :param timeout: int
        :param ignore_case: bool
        :return: str
        """
        times = time.time()
        while time.time() - times < timeout:
            data = self.read_line()
            if ignore_case and re.search(pattern, data, re.IGNORECASE):
                return data
            elif not ignore_case and re.search(pattern, data):
                return data
        return ""

    def read_greps_list(self, keyword, timeout=5, match=PRECISE_MATCH):
        """
        Read data(line by line) grep keyword(All grep)
        :param keyword: str
        :param timeout: int
        :param match: constant
        :return: list
        """
        list_data = []
        times = time.time()
        while time.time() - times < timeout:
            data = self.read_line()
            if match == PRECISE_MATCH and data != "" and keyword in data:
                list_data.append(data)
            elif match == FUZZY_MATCH and data != "" and keyword.upper() in data.upper():
                list_data.append(data)
        return list_data

    def read_greps(self, keyword, timeout=5, match=PRECISE_MATCH):
        """
        Read data(line by line) grep keyword(All grep)
        :param keyword: str
        :param timeout: int
        :param match: constant
        :return: str
        """
        list_data = self.read_greps_list(keyword, timeout, match)
        return "".join(list_data)

    def search(self, command, keyword, timeout=5, match=PRECISE_MATCH):
        """
        Write data and Check read_data
        :param command: str
        :param keyword: str
        :param timeout: int
        :param match: constant
        :return: bool
        """
        self.write(command)
        data = self.read_grep(keyword, timeout, match)
        if data != "":
            return True
        else:
            return False

    def re_search(self, command, pattern, timeout=5, ignore_case=False):
        """

        :param command: str
        :param pattern: str
        :param timeout: int
        :param ignore_case: bool
        :return: bool
        """
        self.write(command)
        data = self.re_read_grep(pattern, timeout, ignore_case)
        print(data)
        if data != "":
            return True
        else:
            return False

    def record_log(self, filename, flush_input=True):
        """
        Record Receive Data At Thread
        :param filename:
        :param flush_input:
        :return:
        """
        if flush_input:
            self.flush_input()
        self._record = True
        fp = open(filename, 'w')
        t = threading.Thread(target=self._record_at_thread, args=(fp,))
        t.setDaemon(True)
        t.start()

    def stop_record(self):
        self._record = False
        time.sleep(1)

    def get_root_permissions(self):
        command_list = ["sitadebug", "sitadebug -t %s" % TFile.get_datetime("%Y%m%d"), "su", "tclsu"]
        for command in command_list:
            self.interrupt()
            self.flush_input()
            self.flush_output()
            if self.search(command, "#", 1) and not self.search("ifconfig", "Permission denied", 1):
                self.write("echo 0 > /proc/sys/kernel/printk")
                self.read_all()
                # time.sleep(1)
                self.write("setprop persist.sys.logd.level V")
                self.read_all()
                # time.sleep(3)
                return True
        return False

