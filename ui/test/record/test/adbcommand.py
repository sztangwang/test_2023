




import subprocess
import time
import threading


import inspect
 
import ctypes
 
def _async_raise(tid, exctype):
 
    """raises the exception, performs cleanup if needed"""
 
    tid = ctypes.c_long(tid)
    if not inspect.isclass(exctype):
        exctype = type(exctype)
 
    res = ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, ctypes.py_object(exctype))
 
    if res == 0:
 
        raise ValueError("invalid thread id")
 
    elif res != 1:
        ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, None)
 
        raise SystemError("PyThreadState_SetAsyncExc failed")
 
def stop_thread(thread):
 
    _async_raise(thread.ident, SystemExit)





def read(p):
    while p.poll() is None and time.time() -start_time<5:
        line = p.stdout.readline()  # 读取数据
        line = str(line, 'UTF-8')  # byte 转 str
        if line:
            print(line)

cmd = ['adb','shell','getevent']
p = subprocess.Popen(cmd, shell=True,  stdout=subprocess.PIPE, stderr=subprocess.PIPE)
start_time = time.time()
t1 = threading.Thread(target=read, args=(p,))
t1.setDaemon(True)
t1.start()
time.sleep(5)
stop_thread(t1)

print('#########')
