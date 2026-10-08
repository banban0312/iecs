from typing import List

from banban.domain.messages import BotMessage
from banban.domain.state import DialogueState
from banban.knowledge.intents import KnowledgeIntent
from banban.knowledge.registry import KnowledgeProviderRegistry
from banban.knowledge.responder import KnowledgeResponder


class KnowledgeHandler:

    def __init__(
            self,
            knowledge_intents:dict[str, KnowledgeIntent],
            provider_registry:KnowledgeProviderRegistry,
            knowledge_responder:KnowledgeResponder
    ):
        self.knowledge_intents = knowledge_intents
        self.provider_registry = provider_registry
        self.knowledge_responder = knowledge_responder

    async def handle(self,intents:list[str],state:DialogueState)->List[BotMessage]:
        # 1.根据intent_id查找对应的provider_ids
        provider_ids = []
        for intent in intents:
            knowledge_intent:KnowledgeIntent = self.knowledge_intents[intent]
            provider_ids.extend(knowledge_intent.provider_ids)
        # 2.去重
        provider_ids = list(set(provider_ids))
        # 3.根据provider_ids找到对应的Provider类实例
        knowledge_chunks = []
        for provider_id in provider_ids:
            provider = self.provider_registry.get(provider_id)
            # 4.使用Provider类实例调用retrieve方法
            chunks =  await provider.retrieve(state)
            knowledge_chunks.extend(chunks)
        # 5.调用KnowledgeResponder生成答案
        return await self.knowledge_responder.respond(state,knowledge_chunks)