import asyncio
import json

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from banban.domain.state import DialogueState
from banban.infrastructure import database
from banban.repository.models.dialogue_state import DialogueStateRecord


class DialogueStateRepository:

    def __init__(self, session:AsyncSession):
        self._session = session

    async def load(self,sender_id: str)->DialogueState:
        # select * from dialogue_state where sender_id = u1001
        result = await self._session.execute(
            select(DialogueStateRecord).where(DialogueStateRecord.sender_id == sender_id)
        )
        # 从结果中获取记录
        record = result.scalar_one_or_none()
        if record is None:
            return DialogueState(sender_id)
        # 如果record有值
        json_str = record.state_json
        dict_data = json.loads(json_str)
        # 将字典数据转换为DialogueState对象
        return DialogueState.from_dict(dict_data)

    async def save(self,state: DialogueState)->None:
        pass


if __name__ == "__main__":
    database.init_db_engine_and_session_factory()

    async def test():
        async with database.session_factory() as session:
            repo = DialogueStateRepository(session)
            state:DialogueState = await repo.load("u1001")
            print("查询结果:", state)

        await database.close_db_engine()

    asyncio.run(test())