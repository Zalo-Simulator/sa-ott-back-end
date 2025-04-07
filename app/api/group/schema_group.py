from pydantic import BaseModel, Field
from typing import List


class CreateNewGroupRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)
    member_ids: List[int] = Field(..., min_items=1)
    type: str = Field(
        ..., regex="^(private|group)$", description="Type of group: private or group"
    )


class CreateNewGroupResponse(BaseModel):
    pass
