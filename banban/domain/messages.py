from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Any


class MessageType(Enum):
    TEXT = "text"
    OBJECT = "object"

@dataclass(slots=True)
class MessageObject:
    type: str
    id: str
    title: str
    attributes: dict[str, Any]

    def to_dict(self)->dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, dict_data)->"MessageObject":
        return cls(**dict_data)


@dataclass(slots=True)
class UserMessage:
    sender_id:str
    message_id:str
    type: MessageType
    text: str | None = None
    object: MessageObject | None = None

    def to_dict(self)->dict:
        return {
            "sender_id": self.sender_id,
            "message_id": self.message_id,
            "type": self.type.value,
            "text": self.text,
            "object": self.object.to_dict() if self.object else None
        }

    @classmethod
    def from_dict(cls, dict_data)->"UserMessage":
        return cls(
            sender_id= dict_data["sender_id"],
            message_id= dict_data["message_id"],
            type= MessageType.TEXT if dict_data["type"] == "text" else MessageType.OBJECT,
            text= dict_data.get("text"),
            object= MessageObject.from_dict(dict_data["object"]) if dict_data.get("object") else None
        )


@dataclass(slots=True)
class BotMessage:
    text:str |None = None
    object:MessageObject | None = None

    def to_dict(self)->dict:
        return {
            "text": self.text,
            "object": self.object.to_dict() if self.object else None
        }

    @classmethod
    def from_dict(cls, dict_data)->"BotMessage":
        return cls(
            text= dict_data.get("text"),
            object= MessageObject.from_dict(dict_data["object"]) if dict_data.get("object") else None
        )



@dataclass(slots=True)
class ProcessResult:
    sender_id:str
    message_id:str
    messages: list[BotMessage] = field(default_factory=list)

    def to_dict(self)->dict:
        return {
            "sender_id": self.sender_id,
            "message_id": self.message_id,
            "messages": [message.to_dict() for message in self.messages]
        }

    @classmethod
    def from_dict(cls, dict_data)->"ProcessResult":
        return cls(
            sender_id= dict_data["sender_id"],
            message_id= dict_data["message_id"],
            messages= [BotMessage.from_dict(message_data) for message_data in dict_data["messages"]]
        )