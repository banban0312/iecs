from typing import Any, Dict

from jinja2 import Template
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate

from banban.domain.messages import BotMessage
from banban.domain.state import DialogueState
from banban.infrastructure.ai_clients import llm_client
from banban.prompts.history_builder import build_history
from banban.prompts.prompt_loader import load_prompt
from banban.task.action.base import Action, ActionResult


class ActionResponse(Action):
    name = "action_response"

    async def run(self, state: DialogueState, args:Dict[str, Any]) -> ActionResult:
        mode = args.get("mode","static")

        if mode == "static":
            # 静态模式创建机器回复
            text = args.get("text","")
            data = {
                "slots": state.active_task.slots if state.active_task else {},
                "context": state.active_system_task.to_dict() if state.active_system_task else {},
            }
            rendered_text = Template(text).render(data)
            return ActionResult(
                messages=[
                    BotMessage(text=rendered_text)
                ]
            )

        elif mode == "rephrase":
            # 改写模式创建机器回复
            # 1.获取text并渲染
            text = args.get("text", "")
            data = {
                "slots": state.active_task.slots if state.active_task else {},
                "context": state.active_system_task.to_dict() if state.active_system_task else {}
            }
            rendered_text = Template(text).render(data)
            # 2.调用LLM对渲染后的回复消息进行改写
            # 模板
            prompt_text = load_prompt("task_action_response_rephrase")
            # 数据
            prompt_inputs = {
                "history": build_history(state.get_current_session().turns),
                "user_message": state.pending_turn.input_message.text,
                "current_response": rendered_text
            }
            # 调用LLM
            # 通过模板构建提示词
            prompt = PromptTemplate.from_template(
                prompt_text,
                template_format="jinja2"
            )
            chain = prompt | llm_client | StrOutputParser()
            rephrased_text = chain.invoke(prompt_inputs)
            # 3.将改写后的文本构造BotMessage并返回
            return ActionResult(
                messages=[BotMessage(text=rephrased_text)]
            )

        else:
            # 生成模式创建机器回复
            # 模板
            prompt_text = load_prompt("task_action_response_generate")
            # 数据
            prompt_inputs = {
                "history": build_history(state.get_current_session().turns),
                "user_message": state.pending_turn.input_message.text
            }
            # 调用LLM
            # 通过模板构建提示词
            prompt = PromptTemplate.from_template(
                prompt_text,
                template_format="jinja2"
            )
            chain = prompt | llm_client | StrOutputParser()
            generated_text = chain.invoke(prompt_inputs)
            # 3.将改写后的文本构造BotMessage并返回
            return ActionResult(
                messages=[BotMessage(text=generated_text)]
            )

