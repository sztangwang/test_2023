from dataclasses import dataclass
from typing import Optional

from dataclasses_json import dataclass_json


@dataclass_json
@dataclass
class DetailData:
    name: str
    value: str
    dataType: int


@dataclass_json
@dataclass
class SocketData:
    """
    数据类
    """
    version: str
    type: int
    #contents: Optional[list[DetailData]]
    contents: Optional[DetailData]

@dataclass_json
@dataclass
class SocketMessage:
    """
    消息类
    """
    cmd: int
    data: SocketData


if __name__ == '__main__':
    temp = []
    data1 = SocketData(version="a", type=1, contents=None)
    data2 = SocketData(version="a", type=1, contents=None)
    temp.append(data1)
    temp.append(data2)


    data = SocketData(version="a", type=1, contents=None)
    print(data.to_json())
    socketdata = SocketData.from_json(data.to_json())
    print(socketdata.type)

    msg = SocketMessage(cmd=0, data=data)
    print(msg.to_json())
    socketmsg = SocketMessage.from_json(msg.to_json())
    print(socketmsg.data)

