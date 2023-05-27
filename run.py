import argparse
import time
from multiprocessing.pool import Pool

import adbutils
import pytest

from compoment.atx2agent.core.common.logs.log_uru import Logger
from compoment.atx2agent.core.tools.adb_utils import get_connect_device

logger = Logger().get_logger
def run_cases(device, retry=0, retry_delay=0):
    """
    :param device:
    """
    cmd = "pytest -s -v --sn={0} --cmdopt={1}".format(device, device)
    logger.info("cmd  ====>>> " + cmd)
    pytest.main(["-s", "-v",  "--cmdopt={0}".format(device)])



def run(devices, retry=3,retry_delay=5):
    if not devices:
        logger.error('There is no device found,test over.')
        return
    logger.info('Starting Run test >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>')
    runs = []
    for i in range(len(devices)):
        runs.append(devices[i])
    pool = Pool(processes=len(runs))
    for run in runs:
        pool.apply_async(run_cases, args=(run,retry,retry_delay))
        time.sleep(2)
    logger.info('Waiting for all runs done........ ')
    pool.close()
    time.sleep(1)
    pool.join()
    logger.info('All runs done........ ')

def connect_devices(udids=None):
    '''get the devices USB connected on PC'''
    serials = [m.serial for m in adbutils.adb.device_list()]  # get all devices serial
    if not udids:
        valid_serials = serials
    else:
        valid_serials = [i for i in udids.split('|') if i in serials]
    if valid_serials:
        logger.info('There has %s devices connected on PC ' % len(valid_serials))
        tmp_list = []
        for serial in valid_serials:
            tmp_list.append(serial)
        return tmp_list
    else:
        logger.error('There is no device connected on PC,please check it.')
        return None

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('-d', '--device', help='device name')
    parser.add_argument('-a', '--app', help='app name')
    parser.add_argument('-t', '--core_test', help='core_test name')
    parser.add_argument('-c', '--case', help='case name')
    parser.add_argument('-P', '--platform', help='platform')
    parser.add_argument('-R', '--robot', help='robot')
    parser.add_argument('-m', '--m', help='pytest mark')
    args = parser.parse_args()


    devices = get_connect_device()
    run(devices, retry=0, retry_delay=5)

