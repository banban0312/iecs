from typing import Any, Dict

from pydantic import BaseModel

class ChatObjectPayload(BaseModel):
    type:str
    id:str
    title:str
    attributes:Dict[str,Any] = {}   # pydantic不支持any，需要使用Any

class ChatHistoryMessageResponse(BaseModel):
    """历史记录中的一条消息"""
    role: str
    text: str|None = None
    object: ChatObjectPayload | None = None

class ChatHistoryResponse(BaseModel):
    sender_id: str
    messages: list[ChatHistoryMessageResponse]

# chat
class ChatRequest(BaseModel):
    sender_id:str
    text: str | None = None
    object: ChatObjectPayload|None = None
    message_id: str | None = None

class BotMessageResponse(BaseModel):
    """客服回复消息"""
    text: str|None = None
    object: ChatObjectPayload | None = None

class ChatResponse(BaseModel):
    sender_id:str
    message_id:str
    messages: list[BotMessageResponse]