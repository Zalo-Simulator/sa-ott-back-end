from pydantic import BaseModel, Field
from typing import List, Optional

from datetime import datetime


class GetChatGroupRequest(BaseModel):
    group_id: int


class MessageDetailPersonSchema(BaseModel):
    id: int
    full_name: Optional[str] = Field(..., min_length=1, max_length=100)
    avatar_url: Optional[str] = Field(..., min_length=0, max_length=200)


class MessageDetailReactionModel(BaseModel):
    id: int
    full_name: Optional[str] = Field(..., min_length=1, max_length=100)
    avatar_url: Optional[str] = Field(..., min_length=0, max_length=200)
    reaction: str
    count: int


class MessageDetailAttachmentModel(BaseModel):
    id: int
    file_url: str
    file_type: str  # image, video, file, sticker
    file_size: Optional[int] = None  # Optional


class MessageDetailSchema(BaseModel):
    person: MessageDetailPersonSchema
    message_id: int
    message: str = Field(..., min_length=1, max_length=250)
    message_type: str
    attachment_id: List[MessageDetailAttachmentModel] = []  # gọi API khác để lấy kaka
    time: datetime
    reactions: List[MessageDetailReactionModel] = []


class GetChatGroupResponse(BaseModel):
    data: list[MessageDetailSchema] = Field(...)


class PostMessageReactionResponse(BaseModel):
    code: str = Field(..., min_length=1, max_length=50)
    message: str = Field(..., min_length=1, max_length=50)
