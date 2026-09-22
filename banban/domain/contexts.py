from dataclasses import dataclass, field
from typing import Any

@dataclass(slots=True)
class TaskContext:
    flow_id: str
    step_id: str
    slots: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class SystemContext:
    """
        所有系统任务上下文的父类(基类)
    """
    flow_id: str
    step_id: str

@dataclass(slots=True)
class StartedSystemContext(SystemContext):
    """
        system_task_started系统任务的上下文
    """
    started_flow_id: str
    started_flow_name: str

@dataclass(slots=True)
class ResumedSystemContext(SystemContext):
    """
        system_task_resumed系统任务的上下文
    """
    resumed_flow_id: str
    resumed_flow_name: str

@dataclass(slots=True)
class CannotHandleSystemContext(SystemContext):
    """
        system_cannot_handle系统任务的上下文
    """

@dataclass(slots=True)
class CollectSystemContext(SystemContext):
    """
        system_collect_information系统任务上下文
    """
    slot_name: str
    response: dict = field(default_factory=dict)

@dataclass(slots=True)
class InterruptedSystemContext(SystemContext):
    """
        system_tast_interrupted系统任务上下文
    """
    interrupted_flow_id: str
    interrupted_flow_name: str
    started_flow_id: str | None = None
    started_flow_name: str | None = None

@dataclass(slots=True)
class CanceledSystemContext(SystemContext):
    """
        system_task_canceled系统任务上下文
    """
    canceled_flow_id: str
    canceled_flow_name: str













