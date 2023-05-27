from dataclasses import dataclass
from typing import Optional

from dataclasses_json import dataclass_json

AGENT_TYPE_DATA = 0
AGENT_TYPE_CHECKBOX = 1


@dataclass_json
@dataclass
class AgentItem:
    name: str
    type: int
    index: int
