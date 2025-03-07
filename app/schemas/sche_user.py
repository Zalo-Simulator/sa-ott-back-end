from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr

from app.helpers.enums import UserRole


class UserBase(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    status: Optional[str] = 'Available'
    is_active: Optional[bool] = True
    role: Optional[str] = UserRole.GUEST

    class Config:
        orm_mode = True

class FriendBase(BaseModel):
    user_id: Optional[str] = None
    friend_id: Optional[EmailStr] = None
    status: Optional[str] = 'Available'
    friend_nick_name: Optional[bool] = True

    class Config:
        orm_mode = True


class UserItemResponse(UserBase):
    id: int
    full_name: str
    email: EmailStr
    is_active: bool
    role: str
    last_login: Optional[datetime]


class UserCreateRequest(UserBase):
    full_name: Optional[str]
    password: str
    email: EmailStr
    is_active: bool = True
    role: UserRole = UserRole.GUEST


class UserRegisterRequest(BaseModel):
    full_name: str
    email: EmailStr
    password: str
    avatar_url: Optional[str] = None
    role: UserRole = UserRole.GUEST


class UserUpdateMeRequest(BaseModel):
    full_name: Optional[str]
    email: Optional[EmailStr]
    password: Optional[str]


class UserUpdateRequest(BaseModel):
    full_name: Optional[str]
    email: Optional[EmailStr]
    password: Optional[str]
    avatar_url: Optional[str]
    status: Optional[str]
    is_active: Optional[bool] = True
    role: Optional[UserRole]

