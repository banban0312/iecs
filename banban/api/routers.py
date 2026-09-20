import uuid

from fastapi import APIRouter, Depends

from banban.api.deps import get_dialogue_service
from banban.api.schemas import ChatHistoryResponse, ChatResponse, ChatRequest, BotMessageResponse, ChatObjectPayload

router = APIRouter()

@router.get("/api/chat/history",response_model=ChatHistoryResponse)
async def get_history(sender_id:str):

    print("sender_id:", sender_id)

    return ChatHistoryResponse(
        (
            {
                "sender_id": "user_001",
                "messages": [
                    {
                        "role": "user",
                        "text": "帮我查一下订单状态",
                        "object": None
                    },
                    {
                        "role": "bot",
                        "text": "请告诉我你的订单号。",
                        "object": None
                    }
                ]
            }
        )
    )

@router.post("/api/chat",response_model=ChatResponse)
async def chat():
    pass