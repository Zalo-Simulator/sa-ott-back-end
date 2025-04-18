import logging
from typing import Any

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm.session import Session
from app.db.base import get_db
from app.exception.zalo_error import ZaloError
from app.helpers.login_manager import login_required
from app.models import User
from app.models.model_group import Group, GroupMember
from app.schemas.sche_base import DataResponse
from app.schemas.sche_group import (
    CreateNewGroupRequest,
    CreateNewGroupResponse,
    GetGroupByGroupIdResponse,
    GetGroupsByUserIdResponse,
    GroupID,
    GroupMemberSimpleResponse,
    GroupMembersResponse,
    GroupsResponse,
    UpdateGroupRequest,
    UpdateGroupResponse,
    UpdateGroupSimpleResponse,
)
from app.services.srv_group import GroupService

router = APIRouter()
logger = logging.getLogger()


@router.post(
    "",
    dependencies=[Depends(login_required)],
    response_model=DataResponse[CreateNewGroupResponse],
)
def create_new_group(
    payload: CreateNewGroupRequest,
    user: User = Depends(login_required),
    db: Session = Depends(get_db),
    group_service: GroupService = Depends(),
) -> Any:
    try:
        group_service.create_group(user, payload=payload, db=db)
        return DataResponse().success_response(data=CreateNewGroupResponse())
    except Exception as e:
        logger.error("Error creating group:%s", e)
        db.rollback()
        raise ZaloError.CANNOT_ADD_MEMBER.as_http_exception()


@router.get(
    "",
    dependencies=[Depends(login_required)],
    response_model=DataResponse[GetGroupsByUserIdResponse],
)
def get_groups_by_user_id(
    group_service: GroupService = Depends(),
    page: int = Query(0, ge=0, description="Page number for pagination"),
    limit: int = Query(10, ge=1, le=100, description="Number of items per page"),
    user: User = Depends(login_required),
    db: Session = Depends(get_db),
) -> Any:
    try:
        res = group_service.get_group_by_user(
            user_id=user.id, page=page, limit=limit, db=db
        )
        return DataResponse().success_response(data=res)
    except Exception as e:
        logger.error("Error getting groups by user id:%s", e)
        raise ZaloError.GROUP_NOT_FOUND.as_http_exception()


@router.get(
    "/private/{friend_id}",
    dependencies=[Depends(login_required)],
    response_model=DataResponse[GroupID],
)
def get_private(
    friend_id: int,
    group_service: GroupService = Depends(),
    user: User = Depends(login_required),
    db: Session = Depends(get_db),
):
    try:
        res = group_service.get_private(user=user, friend_id=friend_id, db=db)
        return DataResponse().success_response(data=res)
    except Exception as e:
        logger.error("Error getting private group:%s", e)
        raise ZaloError.CANNOT_CREATE_GROUP.as_http_exception()


@router.get(
    "/{group_id}",
    dependencies=[Depends(login_required)],
    response_model=DataResponse[GetGroupByGroupIdResponse],
)
def get_group_by_group_id(
    user: User = Depends(login_required),
    group_service: GroupService = Depends(),
    db: Session = Depends(get_db),
    group_id: int = Query(..., description="Group ID"),
) -> Any:
    try:
        res = group_service.get_group_by_group_id(user=user, group_id=group_id, db=db)
        return DataResponse().success_response(data=res)
    except Exception as e:
        logger.error("Error getting group by group id:%s", e)
        raise ZaloError.GROUP_NOT_FOUND.as_http_exception()


@router.put(
    "/{group_id}",
    dependencies=[Depends(login_required)],
    response_model=DataResponse[UpdateGroupSimpleResponse],
)
def update_group(
    group_id: int,
    payload: UpdateGroupRequest,
    group_service: GroupService = Depends(),
    user: User = Depends(login_required),
    db: Session = Depends(get_db),
) -> Any:
    try:
        res = group_service.update_group(
            user=user, group_id=group_id, payload=payload, db=db
        )
        return DataResponse().success_response(data=res)
    except Exception as e:
        logger.error("Error updating group:%s", e)
        db.rollback()
        raise ZaloError.CANNOT_UPDATE_GROUP.as_http_exception()


@router.post(
    "/groups/{id}/members",
    dependencies=[Depends(login_required)],
    response_model=DataResponse[Any],
    deprecated=True,
)
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
