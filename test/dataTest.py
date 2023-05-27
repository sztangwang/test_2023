import json
from dataclasses import dataclass
from typing import Optional

from dataclasses_json import dataclass_json


@dataclass_json
@dataclass
class IdInfo:
    key: str
    name: str
    value: str


@dataclass_json
@dataclass
class Pipeline:
    pipelineId: int
    coreSn: str
    idInfo: str
    bindTime: int


if __name__ == '__main__':
    info_list = []
    info_a = IdInfo("k1", "n1", "v1")
    info_b = IdInfo("k2", "n2", "v3")
    info_c = IdInfo("k3", "n3", "v3")
    info_list.append(info_a.to_dict())
    info_list.append(info_b.to_dict())
    info_list.append(info_c.to_dict())
    json_info_list = json.dumps(info_list)
    print(json_info_list)

    data = Pipeline(1, "sn", idInfo=json_info_list, bindTime=123)
    data_list = []
    data_list.append(data.to_dict())

    out = json.dumps(data_list)
    print(out)
