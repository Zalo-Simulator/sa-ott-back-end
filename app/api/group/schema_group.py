from pydantic import BaseModel, Field
from typing import List, Optional


class CreateNewGroupRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)
    member_ids: List[int] = Field(..., min_items=1)
    type: str = Field(
        ..., regex="^(private|group)$", description="Type of group: private or group"
    )


class CreateNewGroupResponse(BaseModel):
    pass


class GroupMembersResponse(BaseModel):
    id: int
    name: str
    avatar_url: Optional[str] = ""
    role: str
    is_online: bool = False


class GroupsResponse(BaseModel):
    id: int
    name: str
    type: str
    created_by: int
    visible: bool
    member_count: int = 2
    avatar_url: Optional[str] = None
    members: List[GroupMembersResponse] = []


class GetGroupsByUserIdResponse(BaseModel):
    groups: List[GroupsResponse]


class GetGroupByGroupIdResponse(BaseModel):
    id: int
    name: str
    type: str
    created_by: int
    visible: bool
    member_count: int = 2
    avatar_url: Optional[str] = None
    members: List[GroupMembersResponse] = []


class UpdateGroupResponse(BaseModel):
    id: int
    name: str
    type: str
    created_by: int
    visible: bool
    member_count: int = 2
    avatar_url: Optional[str] = None
    members: List[GroupMembersResponse] = []


class UpdateGroupRequest(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=50)
    avatar_url: Optional[str] = Field(None, min_length=1, max_length=255)
