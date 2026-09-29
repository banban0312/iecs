from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, Any, List

from banban.domain.messages import BotMessage
from banban.domain.state import DialogueState

@dataclass(slots=True)
class ActionResult:
    messages: List[BotMessage] = field(default_factory=list)
    slot_updates: Dict[str, Any] = field(default_factory=dict)

class Action(ABC):
    name: str
    @abstractmethod
    # 抽象方法
    async def run(self, state: DialogueState, args: Dict[str, Any])-> ActionResult:
        pass