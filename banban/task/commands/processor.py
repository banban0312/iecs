from requests.packages import target

from banban.domain.state import DialogueState
from banban.task.commands.models import Command, StartFlowCommand, SetSlotsCommand, CancelFlowCommand, ResumeFlowCommand
from banban.task.flows.models import Flow, FlowsList


class CommandProcessor:

    def process_command(self,commands: list[Command],state: DialogueState)->None:
        for command in commands:
            if isinstance(command, StartFlowCommand):
                self._handle_start_flow(command, state)
            elif isinstance(command, SetSlotsCommand):
                self._handle_set_slots(command, state)
            elif isinstance(command, CancelFlowCommand):
                self._handle_cancle_flow(command, state)
            elif isinstance(command, ResumeFlowCommand):
                self._handle_resume_flow(command, state)

    def _handle_start_flow(self,command: StartFlowCommand,state: DialogueState,flows_list:FlowsList):
        flow_id = command.flow
        target_flow: Flow = flows_list.get_flow_by_id(flow_id)

    def _handle_set_slots(self,command: SetSlotsCommand,state: DialogueState):
        pass

    def _handle_cancle_flow(self,command: CancelFlowCommand,state: DialogueState):
        pass

    def _handle_resume_flow(self,command: ResumeFlowCommand,state: DialogueState):
        pass