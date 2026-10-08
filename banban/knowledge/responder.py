from typing import List

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate

from banban.domain.messages import BotMessage
from banban.domain.state import DialogueState
from banban.infrastructure.ai_clients import llm_client
from banban.knowledge.providers import KnowledgeChunk
from banban.prompts.history_builder import build_history, render_user_message
from banban.prompts.prompt_loader import load_prompt


class KnowledgeResponder:

    async def respond(self,state:DialogueState,chunks:List[KnowledgeChunk])->List[BotMessage]:
        # 1.读取提示词模板
        prompt_text = load_prompt("knowledge_respond")
        # 2.提示词参数
        prompt_inputs = {
            "knowledge_content": "\n\n".join([chunk.content for chunk in chunks]),
            "history":build_history(state.get_current_session().turns),
            "user_message":render_user_message(state.pending_turn.input_message)
        }
        # 3.调用LLM
        prompt = PromptTemplate.from_template(
            prompt_text,
            template_format="jinja2"
        )
        chain = prompt | llm_client | StrOutputParser()
        response = await chain.ainvoke(prompt_inputs)
        return [BotMessage(text=response)]