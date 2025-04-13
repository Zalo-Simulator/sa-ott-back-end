from typing import Optional

from pydantic import BaseModel


class GroupBase(BaseModel):
    name: Optional[str] = None
    avatar_url: Optional[str] = None
    type: Optional[str] = None
    visible: Optional[bool] = False

    class Config:
        orm_mode = True


class GroupCreateRequest(GroupBase):
    pass
