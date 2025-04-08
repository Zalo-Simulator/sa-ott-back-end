from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr

from app.helpers.enums import UserRole


class UserBase(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    status: Optional[str] = 'Available'
    is_active: Optional[bool] = True
    avatar_url: Optional[str] = None

    class Config:
        orm_mode = True



class UserItemResponse(BaseModel):
    id: int
    full_name: str
    avatar_url: Optional[str] = None
    is_active: bool

class UserDetailItemResponse(UserBase):
    id: int
    phone: str
    full_name: str
    is_active: bool
    last_login: Optional[datetime]


class UserCreateRequest(UserBase):
    full_name: Optional[str]
    password: str
    is_active: bool = True


class UserRegisterRequest(BaseModel):
    phone: str
    full_name: str
    password: str
    avatar_url: Optional[str] = None


class UserUpdateMeRequest(BaseModel):
    full_name: Optional[str]
    password: Optional[str]


class UserUpdateRequest(BaseModel):
    full_name: Optional[str]
    avatar_url: Optional[str]
    is_active: Optional[bool] = True

