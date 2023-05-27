import time
from dataclasses import dataclass
from typing import Optional

from dataclasses_json import dataclass_json


@dataclass_json
@dataclass
class BaseArgs:
    argsKey: str

    argsValue: str

    argsInfo: str


@dataclass_json
@dataclass
class NettyTaskData:
    taskCode: int
    taskId: int
    result: int
    msg: str
    state: int
    baseArgs: BaseArgs


@dataclass_json
@dataclass
class NettyDeviceData:
    deviceId: int
    deviceSn: str
    systemVersion: str
    deviceState: int
    appVersion: str
    projectName: str


@dataclass_json
@dataclass
class NettyData:
    msgType: int
    deviceData: NettyDeviceData
    nettyTaskDataList: Optional[list[NettyTaskData]] = None


@dataclass_json
@dataclass
class NettyMessage:
    type: int
    timestamp: int
    nettyData: Optional[NettyData] = None


if __name__ == '__main__':
    nettyMessage = NettyMessage(type=1, timestamp=123, nettyData=None)
    print(nettyMessage.to_json())
