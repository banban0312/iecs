import jinja2
from jinja2 import Template
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate

from banban.infrastructure.ai_clients import llm_client


def test1():
    """
    使用原生的jinja2渲染模板
    """
    # 模板
    template_text = "订单{{ slots.order_number }}正在配送中。"
    # 数据
    input_data = {
        "slots": {
            "order_number": "1234567890"
        }
    }
    # 渲染(1.加载模板字符串生成Template实例)
    rendered_text = Template(template_text).render(input_data)
    print(rendered_text)

def test2():
    # 模板
    prompt_text = """你是一个中文电商客服助手，语气自然、友好、简洁。
                  请基于下面的建议回复，生成一句更自然的中文回复。

                  对话上下文：
                  {{ history }}

                  用户最后一句：
                  {{ user_message }}

                  建议回复：
                  {{ current_response }}"""
    # 数据
    prompt_inputs = {
        "history": "用户：你好\n客服：你好！有什么我可以帮忙的吗？",
        "user_message": "我想查询一下我的订单状态",
        "current_response": "您的订单正在配送中。"
    }
    # 通过模板构建提示词
    prompt = PromptTemplate.from_template(
        prompt_text,
        template_format="jinja2"
    )
    chain = prompt | llm_client | StrOutputParser()
    response = chain.invoke(prompt_inputs)
    print(response)

if __name__ == "__main__":
    test2()