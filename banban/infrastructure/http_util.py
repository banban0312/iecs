"""
HTTP 工具模块：封装项目统一的异步 HTTP 客户端。

本模块提供全局异步客户端 http_client，以及初始化与关闭它的函数，
供全项目复用同一个客户端，避免频繁创建 / 销毁连接。
"""
from httpx import AsyncClient

# 全局异步 HTTP 客户端
http_client: AsyncClient | None = None


def init_http_client():
    """
    初始化全局 HTTP 客户端。
    """
    global http_client
    http_client = AsyncClient()


async def close_http_client():
    """
    关闭全局 HTTP 客户端，释放连接资源。
    """
    await http_client.aclose()