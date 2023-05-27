from dataclasses import dataclass

from PyQt5.QtCore import Qt, QThread
from dataclasses_json import dataclass_json
from compoment.atx2agent.core.models.model import CaseDto

@dataclass_json
@dataclass
class Device:
    OFFLINE = 0
    ONLINE = 1
    # 繁忙
    BUSY = 2
    # 空闲
    IDLE = 3

    serialsName: str
    info: str
    connectionState: int
    projectName: str
    checkState: Qt.CheckState
    runnable: any

class TaskStatus:
    PENDING = 'Pending'
    RUNNING = 'Running'
    FINISHED = 'Finished'
    CANCELLING = 'Cancelling'
    CANCELLED = 'Cancelled'
    FAILED = 'Failed'
    TIMEOUT = 'Timeout'

class TaskType:
    KW_UI_TEST = "KW_UI_TEST"  # UI测试任务
    SMOKE_TEST = "SMOKE_TEST"  # 冒烟测试任务
    HARDWARE_TEST = "HARDWARE_TEST"  # 硬件测试任务
    PO_UI_TEST = "PO_UI_TEST"  # PageObject 模式的UI任务
    NONE = "NONE"  # 无任务

@dataclass_json
@dataclass
class Task:
    task_id: int = 0
    task_name: str = ''
    test_cases: list[CaseDto] = None
    device: Device = None
    task_type: str = ''
    status: str = ''
    result: str = ''
    task_thread: QThread = None
    task_timeout: int = 300

