from dataclasses import dataclass, field
from typing import Any

from banban.domain.contexts import TaskContext, SystemContext
from banban.domain.messages import BotMessage


@dataclass(slots=True)
class FocusedObject:
    """
        聚焦对象
    """
    type: str
    id: str
    title: str
    attributes: dict[str, Any] = field(default_factory=dict)

@dataclass(slots=True)
class Turn:
    """
        对话轮次: 一个Turn实例表示一轮对话
    """
    turn_id: str
    input_message: str
    assistant_messages: list[BotMessage] = field(default_factory=list)

@dataclass(slots=True)
class Session:
    """
        用户会话:当两条消息之间的时间间隔超过[1小时]时，会话结束
    """
    session_id: str
    created_at: float
    last_activity_at: float
    closed_at: float
    turns: list[Turn] = field(default_factory=list)

@dataclass(slots=True)
class DialogueState:
    sender_id: str
    active_task: TaskContext | None = None
    paused_tasks: list[TaskContext] = field(default_factory=list)
    active_system_task: SystemContext | None = None
    focused_object: FocusedObject | None = None
    sessions: list[Session] = field(default_factory=list)
    current_session_id: str | None = None
    pending_turn: Turn | None = None












