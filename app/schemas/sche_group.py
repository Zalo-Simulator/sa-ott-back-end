from datetime import datetime
from typing import Optional, List 

from pydantic import BaseModel, EmailStr

from app.helpers.enums import UserRole

class GroupBase(BaseModel):
    name: Optional[str] = None
    avatar_url: Optional[str] = None
    type: Optional[str] = None
    visible: Optional[bool] = False

    class Config:
        orm_mode = True

class GroupCreateRequest(GroupBase):
    pass

