from typing import Optional
from pydantic import BaseModel
from typing import List
from app.schemas.sche_user import UserDetailItemResponse

class FriendBase(BaseModel):
    user_id: Optional[int] = None
    friend_id: Optional[int] = None
    status: Optional[str] = None
    friend_nick_name: Optional[str] = None

    class Config:
        orm_mode = True
class FriendSchemaResponse(FriendBase):
    id: int
    user_id: int
    friend_id: int
    status: str
    friend_nick_name: Optional[str]  # Optional field

class FriendsListResponse(BaseModel):
    friends: List[UserDetailItemResponse]

class CreateFriendRequest(BaseModel):
    user_id: int
    friend_id: int
    status: str = "pending"
    friend_nick_name: Optional[str]

class UpdateFriendRequest(BaseModel):
    user_id: Optional[int]
    friend_id: Optional[int]
    status: Optional[str] = "pending"
    friend_nick_name: Optional[str]