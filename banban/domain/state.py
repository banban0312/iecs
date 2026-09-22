import time
from dataclasses import dataclass, field
from typing import Any

from banban.domain.contexts import TaskContext, SystemContext
from banban.domain.messages import BotMessage, UserMessage


@dataclass(slots=True)
class FocusedObject:
    """
        聚焦对象
    """
    type: str
    id: str
    title: str
    attributes: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, raw_focused: dict[str, Any])->"FocusedObject":
        return cls(**raw_focused)


@dataclass(slots=True)
class Turn:
    """
        对话轮次: 一个Turn实例表示一轮对话
    """
    turn_id: str
    input_message: UserMessage
    assistant_messages: list[BotMessage] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data)->"Turn":
        return cls(
            turn_id = data.get("turn_id"),
            input_message = UserMessage.from_dict(data["input_message"]),
            assistant_messages = [BotMessage.from_dict(bot_message) for bot_message in data.get("assistant_messages", [])],
        )



@dataclass(slots=True)
class Session:
    """
        用户会话:当两条消息之间的时间间隔超过[1小时]时，会话结束
    """
    session_id: str
    started_at: float
    last_activity_at: float
    closed_at: float
    turns: list[Turn] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data)->"Session":
        return cls(
            session_id = data.get("session_id"),
            started_at = data.get("started_at", time.time()),
            last_activity_at = data.get("last_activity_at", time.time()),
            closed_at = data.get("closed_at"),
            turns = [Turn.from_dict(turn_data) for turn_data in data.get("turns", [])],
        )


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

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "DialogueState":
        """从字典还原 DialogueState。"""
        state = cls(sender_id=data["sender_id"])
        # 当前用户任务
        raw_task = data.get("active_task")
        state.active_task = TaskContext.from_dict(raw_task) if raw_task else None
        # 挂起的任务
        state.paused_tasks = [TaskContext.from_dict(task) for task in data.get("paused_tasks", [])]
        # 系统任务
        raw_sys = data.get("active_system_task")
        state.active_system_task = SystemContext.from_dict(raw_sys) if raw_sys else None
        # 聚焦对象
        raw_focused = data.get("focused_object")
        state.focused_object = FocusedObject.from_dict(raw_focused) if raw_focused else None
        # 会话列表
        state.sessions = [Session.from_dict(session_data) for session_data in data.get("sessions", [])]
        # 当前会话id
        state.current_session_id = data.get("current_session_id")
        # 返回从字典还原成DialogueState对象的state
        return state







