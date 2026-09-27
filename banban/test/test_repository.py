import asyncio

from banban.domain.state import DialogueState, FocusedObject
from banban.infrastructure import database
from banban.repository.dialogue_state_repository import DialogueStateRepository


def test_load():
    database.init_db_engine_and_session_factory()

    async def test():
        async with database.session_factory() as session:
            repo = DialogueStateRepository(session)
            state:DialogueState = await repo.load("u1002")
            print("查询结果:", state.to_dict())

        await database.close_db_engine()

    asyncio.run(test())


def test_save():
    database.init_db_engine_and_session_factory()
    async def test():
        async with database.session_factory() as session:
            repo = DialogueStateRepository(session)
            # 测试1： 存在用户对话状态
            state = DialogueState(
                sender_id="u1004",
                active_task=None,
                paused_tasks=[],
                active_system_task=None,
                focused_object=FocusedObject(
                    type="order",
                    id="A202600001",
                    title="羽毛球拍",
                    attributes={"price": "1000", "quantity": "1"}
                )
            )

            await repo.save(state)

        await  database.close_db_engine()
    asyncio.run(test())

if __name__ == "__main__":
    test_save()