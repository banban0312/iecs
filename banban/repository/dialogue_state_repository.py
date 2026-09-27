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

    async def save(self,state:DialogueState)->None:
        """
        更新对话状态
        """
        # 1.将state转换成json格式字符串结构
        dict_data = state.to_dict()
        json_str = json.dumps(dict_data,ensure_ascii=False)

        # 2.根据state.sender_id查询用户状态
        result = await self._session.execute(
            select(DialogueStateRecord).where(DialogueStateRecord.sender_id == state.sender_id)
        )
        record = result.scalar_one_or_none()
        # 3.判断用户状态
        if record is None:
            #   如果没有查询到结果，则插入新用户状态
            self._session.add(
                DialogueStateRecord(
                    sender_id=state.sender_id, state_json=json_str
                )
            )
        else:
            #   如果查询到了结果，则更新用户状态
            record.state_json = json_str

        await self._session.commit()