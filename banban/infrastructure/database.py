"""
数据库模块：基于 SQLAlchemy 封装异步数据库引擎与会话工厂。

本模块提供全局的异步引擎 engine 和会话工厂 session_factory，
以及初始化与关闭它们的函数，供全项目复用。
"""
from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker, AsyncSession, create_async_engine

from banban.conf.config import settings

# 全局异步数据库引擎
engine : AsyncEngine | None = None

# 全局异步会话工厂
session_factory : async_sessionmaker[AsyncSession] | None = None

def init_db_engine_and_session_factory():
    """
    初始化全局数据库引擎与会话工厂。

    创建异步引擎（含连接池配置），并基于该引擎构建会话工厂，
    结果赋值给模块级变量 engine 与 session_factory。
    """
    global engine, session_factory
    engine = create_async_engine(
        url=settings.database_url,      # 数据库连接串
        echo=True,                      # 是否开启 SQL 日志
        pool_size=10,                   # 连接池大小
        pool_pre_ping=False,            # 是否开启连接预检查
    )
    session_factory = async_sessionmaker(
        engine,
        expire_on_commit=False,         # 提交后对象不过期，可继续访问属性
    )

async def close_db_engine():
    """
    关闭全局数据库引擎，释放连接池资源。
    """
    if engine is not None:
        await engine.dispose()