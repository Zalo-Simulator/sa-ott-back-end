from pydantic import BaseModel, Field
from typing import List

from datetime import datetime


class GetChatGroupRequest(BaseModel):
    pass


class MessageDetailPersonSchema(BaseModel):
    id: int
    full_name: str = Field(..., min_length=1, max_length=100)
    avatar_url: str = Field(..., min_length=1, max_length=200)


class MessageDetailReactionModel(BaseModel):
    id: int
    full_name: str = Field(..., min_length=1, max_length=100)
    avatar_url: str = Field(..., min_length=1, max_length=200)
    reaction: str
    count: int


class MessageDetailSchema(BaseModel):
    person: MessageDetailPersonSchema
    message: str = Field(..., min_length=1, max_length=250)
    message_type: str
    attachment_id: str  # gọi API khác để lấy kaka
    time: datetime
    reactions: List[MessageDetailReactionModel] = []


class GetChatGroupResponse(BaseModel):
    code: str = Field(..., min_length=1, max_length=50)
    message: str = Field(..., min_length=1, max_length=50)
    data: list[MessageDetailSchema] = Field(...)


class PostMessageReactionResponse(BaseModel):
    code: str = Field(..., min_length=1, max_length=50)
    message: str = Field(..., min_length=1, max_length=50)
