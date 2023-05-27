from dataclasses import dataclass
from typing import Optional

from dataclasses_json import dataclass_json
import socket


@dataclass_json
@dataclass
class Connection:
    socket: socket
    sid: int
    deviceId: str
