from typing import Optional
from pydantic import BaseModel
from typing import List

class FriendSchemaResponse(BaseModel):
    user_id: int
    friend_id: int
    status: str
    friend_nick_name: Optional[str]  # Optional field

class FriendsListResponse(BaseModel):
    friends: List[FriendSchemaResponse]

class CreateFriendRequest(BaseModel):
    user_id: int
    friend_id: int
    status: str = "pending"
    friend_nick_name: Optional[str]

class UpdateFriendRequest(BaseModel):
    user_id: int
    friend_id: int
    status: str = "pending"
    friend_nick_name: Optional[str]