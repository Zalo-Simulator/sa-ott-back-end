from typing import Any

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.group.schema_group import (
    CreateNewGroupRequest,
    CreateNewGroupResponse,
    GetGroupsByUserIdResponse,
    GroupsResponse,
)
from app.db.base import get_db
from app.exception.zalo_error import ZaloError
from app.helpers.login_manager import login_required
from app.models import User
from app.models.model_group import Group, GroupMember
from app.schemas.sche_base import DataResponse

router = APIRouter()


@router.post("/", response_model=DataResponse[CreateNewGroupResponse])
def create_new_group(
    payload: CreateNewGroupRequest,
    user: User = Depends(login_required),
    db: Session = Depends(get_db),
) -> Any:
    try:
        group = Group(
            name=payload.name,
            created_by=user.id,
            type=payload.type,
            visible=False if payload.type == "private" else True,
        )
        db.add(group)
        db.commit()
        db.refresh(group)

        # Add group members
        group_member = GroupMember(
            group_id=group.id,
            user_id=user.id,
            role="admin",
        )
        db.add(group_member)
        db.commit()
        db.refresh(group_member)

        # Add other members
        for member_id in payload.member_ids:
            if member_id == user.id:
                continue
            group_member = GroupMember(
                group_id=group.id,
                user_id=member_id,
                role="member",
            )
            db.add(group_member)
            db.commit()
            db.refresh(group_member)
        return DataResponse().success_response(data=CreateNewGroupResponse())
    except Exception as e:
        print("Error creating group:", e)
        raise ZaloError.CANNOT_UPLOAD_FILE.as_http_exception()


@router.get("/", response_model=DataResponse[GetGroupsByUserIdResponse])
def get_groups_by_user_id(
    page: int = Query(1, ge=0, description="Page number for pagination"),
    limit: int = Query(10, ge=1, le=100, description="Number of items per page"),
    user: User = Depends(login_required),
    db: Session = Depends(get_db),
) -> Any:
    db_group_members = (
        db.query(GroupMember)
        .filter(GroupMember.user_id == user.id)
        .limit(limit)
        .offset(page)
        .all()
    )
    return DataResponse().success_response(
        data=GetGroupsByUserIdResponse(
            groups=[
                GroupsResponse(
                    id=group_member.group_id,
                    name=group_member.group.name,
                    type=group_member.group.type,
                    created_by=group_member.group.created_by,
                    visible=group_member.group.visible,
                    member_count=len(group_member.group.members),
                    avatar_url=group_member.group.avatar_url,
                )
                for group_member in db_group_members
            ]
        )
    )
