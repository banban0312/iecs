"""
测试模块：用于验证 AI 客户端（llm_client）的基本调用。

本模块向大语言模型发送一条消息，并打印模型返回的文本内容。

必要前置条件：
    - 配置中提供真实有效的 API Key 与模型服务 URL
"""
from banban.infrastructure.ai_clients import llm_client

if __name__ == "__main__":
    # 同步调用 LLM，传入用户消息 "你好"
    response = llm_client.invoke("你好")
    # 打印模型返回的文本内容
    print(response.content)