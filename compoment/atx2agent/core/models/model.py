from dataclasses import dataclass, field
from typing import Optional, Dict, List
from dataclasses_json import dataclass_json


@dataclass_json
@dataclass
class LocatorDto:
    name: str
    locatorType: str
    locatorValue: str
    locateDesc: Optional[str] = None

@dataclass_json
@dataclass
class StepDto:
    name: str
    desc: str
    action: str
    params: Optional[Dict[str, str]] = None
    locators: Optional[List[LocatorDto]] = None

@dataclass_json
@dataclass
class GlobalValDto:
    name: str
    value: str

@dataclass_json
@dataclass
class PreStepDto:
    step: StepDto

@dataclass_json
@dataclass
class PostStepDto:
    step: StepDto

@dataclass_json
@dataclass
class StepsDto:
    step: StepDto

@dataclass_json
@dataclass
class CaseDto:
    caseId: int
    name: str
    desc: str
    level:Optional[str]
    status:Optional[str]
    globalVal: List[GlobalValDto]
    presteps: List[PreStepDto]
    poststeps: List[PostStepDto]
    steps: List[StepsDto]

@dataclass_json
@dataclass
class Case:
    case: CaseDto

@dataclass_json
@dataclass
class CasesDto:
    cases: List[Case] = field(default_factory=list)


@dataclass_json
@dataclass
class ModuleDto:
    name: str
    cases: List[Case] = field(default_factory=list)

@dataclass_json
@dataclass
class ModulesDto:
    module: ModuleDto


@dataclass_json
@dataclass
class ProjectDto:
    name: str
    project_case_type:str
    modules: List[ModulesDto] =field(default_factory=list)

@dataclass_json
@dataclass
class ProjectD:
    project: ProjectDto


