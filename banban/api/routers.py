import uuid

from fastapi import APIRouter, Depends

from banban.api.deps import get_dialogue_service
from banban.api.schemas import ChatHistoryResponse, ChatResponse, ChatRequest, BotMessageResponse, ChatObjectPayload
from banban.domain.messages import UserMessage, ProcessResult
from banban.service.dialogue_service import DialogueService

router = APIRouter()

@router.get("/api/chat/history",response_model=ChatHistoryResponse)
async def get_history(sender_id:str):

    print("sender_id:", sender_id)

    return ChatHistoryResponse(
        sender_id = sender_id,
        messages = [

        ]
    )



    # return {
    #     "sender_id": "user_001",
    #     "messages": [
    #         {
    #             "role": "user",
    #             "text": "帮我查一下订单状态",
    #             "object": None
    #         },
    #         {
    #             "role": "bot",
    #             "text": "请告诉我你的订单号。",
    #             "object": None
    #         }
    #     ]
    # }

@router.post("/api/chat",response_model=ChatResponse)
async def chat(
        chat_request:ChatRequest,
        dialogue_service:DialogueService = Depends( get_dialogue_service )
):
    # 1.将交互模型chat_request 转换成 领域模型 UserMessage
    dict_data = {
        "sender_id": chat_request.sender_id,
        "message_id": chat_request.message_id if chat_request.message_id else str(uuid.uuid4()),
        "type": "text" if chat_request.text else "object",
        "text": chat_request.text,
        "object": {
            "type": chat_request.object.type,
            "id": chat_request.object.id,
            "title": chat_request.object.title,
            "attributes": chat_request.object.attributes
        } if chat_request.object else None
    }
    user_message = UserMessage.from_dict(dict_data)

    # 2.调用DialogueService类中的process_message方法进行对话处理
    process_result:ProcessResult = dialogue_service.process_message(user_message)

    # 3.将领域模型 process_result 转换成交互模型 ChatResponse
    messages = []
    for bot_message in process_result.messages:
        bot_message_response = BotMessageResponse(
            text=bot_message.text,
            object = ChatObjectPayload(
                type=bot_message.object.type,
                id=bot_message.object.id,
                title=bot_message.object.title,
                attributes=bot_message.object.attributes
            ) if bot_message.object is not None else None
        )
        messages.append(bot_message_response)

    chat_response = ChatResponse(
        sender_id= process_result.sender_id,
        message_id= process_result.message_id,
        messages= messages
    )
    # 4.返回交互模型 ChatResponse
    return chat_response