from typing import Dict, Any

from banban.domain.state import DialogueState
from banban.task.action.base import Action, ActionResult


class ActionListen(Action):
    name = "action_listen"
    async def run(self, state:DialogueState, args:Dict[str,Any]) ->ActionResult:
        pass