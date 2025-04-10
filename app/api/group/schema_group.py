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


class GroupsResponse(BaseModel):
    id: int
    name: str
    type: str
    created_by: int
    visible: bool
    member_count: int = 2
    avatar_url: Optional[str] = None


class GetGroupsByUserIdResponse(BaseModel):
    groups: List[GroupsResponse]
