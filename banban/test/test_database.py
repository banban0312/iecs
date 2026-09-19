"""
测试模块：用于验证数据库引擎与会话工厂的初始化、连接与查询。

本模块演示了如何使用项目中的异步数据库工具（database）创建会话，
执行一条简单 SQL（select 1），并打印查询结果。

必要启动模块：
    - 数据库服务

导入方式说明：
    本模块使用 `from ... import database` 导入模块对象，而非
    `from database import session_factory, init_db_engine_and_session_factory, ...`
    导入成员。原因是 session_factory 属于模块内可变的全局状态：它在模块加载时
    为 None，由 init_db_engine_and_session_factory() 重新赋值。若直接导入
    session_factory，拿到的是赋值前的旧引用（None），无法感知后续变化。
    只有通过 database.session_factory 这种属性访问，才能始终取到最新值。
"""
import asyncio

from sqlalchemy import text

from banban.infrastructure import database


async def test():
    """
    异步测试函数：连接数据库并执行一条简单查询。

    执行流程：
        1. 初始化全局数据库引擎与会话工厂。
        2. 开启一个异步会话。
        3. 执行 SQL：select 1。
        4. 打印查询结果。
        5. 关闭数据库引擎，释放连接资源。

    注意：
        session_factory 必须通过 database.session_factory 访问，而不是提前
        from ... import session_factory，否则会拿到 None。
    """
    # 初始化数据库引擎与会话工厂（内部会重新赋值 database.session_factory）
    database.init_db_engine_and_session_factory()

    # 通过模块属性访问，确保取到初始化后的会话工厂
    async with database.session_factory() as session:
        # 执行一条简单 SQL，验证连接可用
        result = await session.execute(text("select 1"))
        # 打印查询结果
        print(result.all())

    # 关闭数据库引擎，释放资源
    await database.close_db_engine()


if __name__ == '__main__':
    # 启动事件循环运行 test 协程
    asyncio.run(test())