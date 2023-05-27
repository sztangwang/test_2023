from dataclasses import dataclass
from typing import Optional

from PyQt5.QtCore import Qt
from dataclasses_json import dataclass_json


@dataclass_json
@dataclass
class Device:
    OFFLINE = 0
    ONLINE = 1

    serialsName: str
    info: str
    connectionState: int
    projectName: str
    checkState: Qt.CheckState
    runnable: any
