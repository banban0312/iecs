from pathlib import Path

from banban.engine.dialogue_engine import DialogueEngine
from banban.knowledge.handle import KnowledgeHandler
from banban.knowledge.intents import KNOWLEDGE_INTENTS
from banban.knowledge.providers import ProductAPIProvider, OrderAPIProvider, FAQProvider, RAGProvider
from banban.knowledge.registry import KnowledgeProviderRegistry
from banban.knowledge.responder import KnowledgeResponder
from banban.task.action.builder import build_action_runner
from banban.task.commands.processor import CommandProcessor
from banban.task.flows.executor import FlowExecutor
from banban.task.flows.loader import FlowLoader
from banban.task.handler import TaskHandler


def build_dialogue_engine()->DialogueEngine:
    # 加载flows
    user_flows_path = Path(__file__).parents[2] / 'flow_config' / 'user_flows.yml'
    system_flows_path = Path(__file__).parents[2] / 'flow_config' / 'system_flows.yml'
    loader = FlowLoader()
    flows_list = loader.load_many([user_flows_path, system_flows_path])
    # 1.创建TaskHandler示例
    task_handler = TaskHandler(
        processor = CommandProcessor(),
        executor= FlowExecutor(
            runner = build_action_runner()
        ),
        flowslist = flows_list
    )

    # 2.创建KnowledgeHandler实例
    knowledge_handler = KnowledgeHandler(
        knowledge_intents = KNOWLEDGE_INTENTS,
        provider_registry = KnowledgeProviderRegistry([
            ProductAPIProvider(),
            OrderAPIProvider(),
            FAQProvider(),
            RAGProvider()
        ]),
        knowledge_responder = KnowledgeResponder()
    )
    return DialogueEngine(
        task_handler = task_handler,
        knowledge_handler = knowledge_handler,
    )