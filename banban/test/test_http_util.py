"""
测试模块：用于验证 HTTP 客户端工具与订单服务的集成调用。

本模块演示了如何使用项目中的异步 HTTP 工具（http_util）发起一次
GET 请求，访问 commerce API 中某个用户的订单列表接口。

必要启动模块：
    - commerce API 原生业务后端服务

导入方式说明：
    本模块使用 `from ... import http_util` 导入模块对象，而非
    `from http_util import http_client, init_http_client, ...` 导入成员。
    原因是 http_client 属于模块内可变的全局状态：它在模块加载时为 None，
    由 init_http_client() 重新赋值。若直接导入 http_client，拿到的是赋值
    前的旧引用（None），无法感知后续变化。只有通过 http_util.http_client
    这种属性访问，才能始终取到模块中的最新值。
"""
import asyncio

from banban.conf.config import settings
from banban.infrastructure import http_util


async def test():
    """
    异步测试函数：调用用户订单接口并打印返回结果。

    执行流程：
        1. 初始化全局 HTTP 客户端。
        2. 发起 GET 请求，访问 {commerce_api_base_url}/users/u1001/orders。
        3. 打印响应体中的 JSON 数据。
        4. 关闭 HTTP 客户端，释放连接资源。

    注意：
        http_client 必须通过 http_util.http_client 访问，而不是提前
        from ... import http_client，否则会拿到 None。
    """
    # 初始化 HTTP 客户端（内部会重新赋值 http_util.http_client）
    http_util.init_http_client()
    # 通过模块属性访问，确保取到初始化后的客户端
    result = await http_util.http_client.get(f'{settings.commerce_api_base_url}/users/u1001/orders')
    # 打印接口返回的 JSON 数据
    print(result.json())
    # 关闭 HTTP 客户端，释放资源
    await http_util.close_http_client()


if __name__ == "__main__":
    # 启动事件循环运行 test 协程
    asyncio.run(test())