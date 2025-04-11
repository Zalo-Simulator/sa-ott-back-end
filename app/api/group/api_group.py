from typing import Any

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.group.schema_group import (
    CreateNewGroupRequest,
    CreateNewGroupResponse,
    GetGroupsByUserIdResponse,
    GroupsResponse,
    GroupMembersResponse,
    GetGroupByGroupIdResponse,
    UpdateGroupResponse,
    UpdateGroupRequest,
)
from app.db.base import get_db
from app.exception.zalo_error import ZaloError
from app.helpers.login_manager import login_required
from app.models import User
from app.models.model_group import Group, GroupMember
from app.schemas.sche_base import DataResponse
from app.helpers.logging import logger

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
    except Exception:
        db.rollback()
        raise ZaloError.CANNOT_CREATE_GROUP.as_http_exception()

    # TODO: Verify they are friends

    try:
        # Add group members
        group_member = GroupMember(
            group_id=group.id,
            user_id=user.id,
            role="admin",
        )
        db.add(group_member)
        db.commit()
        db.refresh(group_member)
    except Exception:
        db.rollback()
        raise ZaloError.CANNOT_ACCESS_ADMIN_GROUP.as_http_exception()

    try:
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
        logger.error("Error creating group:", e)
        db.rollback()
        raise ZaloError.CANNOT_ADD_MEMBER.as_http_exception()


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
                    members=[
                        GroupMembersResponse(
                            id=member.user_id,
                            name=member.user.full_name,
                            avatar_url=member.user.avatar_url,
                            role=member.role,
                            is_online=member.user.is_online,
                        )
                        for member in group_member.group.members
                    ],
                )
                for group_member in db_group_members
            ]
        )
    )


@router.get("/{group_id}", response_model=DataResponse[GetGroupByGroupIdResponse])
def get_group_by_group_id(
    user: User = Depends(login_required),
    db: Session = Depends(get_db),
    group_id: int = Query(..., description="Group ID"),
) -> Any:
    db_group = db.query(Group).filter(Group.id == group_id).first()
    if not db_group:
        raise ZaloError.GROUP_NOT_FOUND.as_http_exception()

    if not db_group.visible:  # if it is a private group and user is not a member
        is_member = (
            db.query(GroupMember)
            .filter(GroupMember.group_id == group_id, GroupMember.user_id == user.id)
            .first()
        )
        if not is_member:
            raise ZaloError.GROUP_PERMISSION_DENIED.as_http_exception()

    db_group_members = (
        db.query(GroupMember).filter(GroupMember.group_id == group_id).all()
    )

    return DataResponse().success_response(
        data=GetGroupByGroupIdResponse(
            id=db_group.id,
            name=db_group.name,
            type=db_group.type,
            created_by=db_group.created_by,
            visible=db_group.visible,
            member_count=len(db_group_members),
            avatar_url=db_group.avatar_url,
            members=[
                GroupMembersResponse(
                    id=member.user_id,
                    name=member.user.full_name,
                    avatar_url=member.user.avatar_url,
                    role=member.role,
                    is_online=member.user.is_online,
                )
                for member in db_group_members
            ],
        )
    )


@router.put("/{group_id}", response_model=DataResponse[UpdateGroupResponse])
def update_group(
    group_id: int,
    payload: UpdateGroupRequest,
    user: User = Depends(login_required),
    db: Session = Depends(get_db),
) -> Any:
    db_group = db.query(Group).filter(Group.id == group_id).first()
    if not db_group:
        raise ZaloError.GROUP_NOT_FOUND.as_http_exception()

    # Verify that an user is a member
    is_member = (
        db.query(GroupMember)
        .filter(GroupMember.group_id == group_id, GroupMember.user_id == user.id)
        .first()
    )
    if not is_member:
        raise ZaloError.GROUP_PERMISSION_DENIED.as_http_exception()

    db_group.name = payload.name
    db_group.avatar_url = payload.avatar_url
    db.commit()
    db.refresh(db_group)

    return DataResponse().success_response(
        data=UpdateGroupResponse(
            id=db_group.id,
            name=db_group.name,
            type=db_group.type,
            created_by=db_group.created_by,
            visible=db_group.visible,
            member_count=len(db_group.members),
            avatar_url=db_group.avatar_url,
            members=[
                GroupMembersResponse(
                    id=member.user_id,
                    name=member.user.full_name,
                    avatar_url=member.user.avatar_url,
                    role=member.role,
                    is_online=member.user.is_online,
                )
                for member in db_group.members
            ],
        )
    )


@router.post("/groups/{id}/members", response_model=DataResponse[Any], deprecated=True)
def add_group_member(
    id: int,
    user_id: int,
    user: User = Depends(login_required),
    db: Session = Depends(get_db),
) -> Any:
    """
    API Add member to group
    """
    # TODO


@router.delete(
    "/groups/{id}/members/{user_id}",
    response_model=DataResponse[Any],
    deprecated=True,
)
def remove_group_member(
    id: int,
    user_id: int,
    user: User = Depends(login_required),
    db: Session = Depends(get_db),
) -> Any:
    """
    API Remove member from group
    """
    # TODO
