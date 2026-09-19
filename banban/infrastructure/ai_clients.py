"""
AI 客户端模块：封装项目统一的大语言模型（LLM）调用入口。

本模块基于 LangChain 的 init_chat_model 创建全局 LLM 客户端 llm_client，
模型名称、服务地址、API Key 等参数均从 settings 中读取。
"""
from langchain.chat_models import init_chat_model

from banban.conf.config import settings

# 创建全局 LLM 客户端单例，供全项目导入使用
llm_client = init_chat_model(
    model = settings.llm_model,           # 模型名称
    base_url = settings.llm_base_url,     # 模型服务地址
    api_key = settings.llm_api_key,       # 模型服务 API Key
    model_provider = "openai",            # 模型提供方
    # 采样温度：控制输出的随机性。
    # 取值越低（如 0）输出越确定、稳定，适合问答、抽取、分类等需要可复现的场景；
    # 取值越高（如 1.0 以上）输出越发散、有创意，适合写作、头脑风暴。
    temperature = 0,
)