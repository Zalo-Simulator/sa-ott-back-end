import logging
from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException
from fastapi_sqlalchemy import db

from app.helpers.exception_handler import CustomException
from app.helpers.login_manager import login_required, PermissionRequired
from app.helpers.paging import Page, PaginationParams, paginate
from app.schemas.sche_base import DataResponse
from app.schemas.sche_user import (
    UserItemResponse,
    UserDetailItemResponse,
    UserCreateRequest,
    UserUpdateMeRequest,
    UserUpdateRequest,
)
from app.schemas.sche_friend import (
    FriendsListResponse,
    FriendSchemaResponse
)
from app.services.srv_user import UserService
from app.services.srv_friend import FriendService
from app.models import User
from app.exception.user_error import UserError

logger = logging.getLogger()
router = APIRouter()


@router.get(
    "/{id}",
    dependencies=[Depends(login_required)],
    response_model=DataResponse[UserDetailItemResponse],
)
def get_user_detail(id: int, user_service: UserService = Depends()) -> Any:
    """
    API Get User information
    """
    try:
        return DataResponse().success_response(data=user_service.get_detail(id))
    except Exception:
        raise UserError.CANNOT_GET_USER_DETAIL.as_http_exception()

@router.put(
    "/{id}",
    dependencies=[Depends(login_required)],
    response_model=DataResponse[UserItemResponse],
)
def update_user(
    id: int, user_data: UserUpdateRequest, user_service: UserService = Depends()
) -> Any:
    """
    API Update User information
    """
    try:
        updated_user = user_service.update(user_id=id, data=user_data)
        return DataResponse().success_response(data=updated_user)
    except Exception:
        raise UserError.CANNOT_UPDATE_USER_ACCOUNT.as_http_exception()


@router.get(
    "/{id}/contacts",
    dependencies=[Depends(login_required)],
    response_model=DataResponse[FriendsListResponse],
)
def get_user_contacts(id: int, user_service: UserService = Depends()) -> Any:
    """
    API Get User's contacts
    """
    try:
        contacts = user_service.get_contacts(id)
        return DataResponse().success_response(data=contacts)
    except Exception:
        raise UserError.CANNOT_GET_USER_CONTACTS.as_http_exception()

@router.get(
    "/{id}/contacts/pending",
    dependencies=[Depends(login_required)],
    response_model=DataResponse[FriendsListResponse],
)
def get_user_pending_contacts(id: int, user_service: UserService = Depends()) -> Any:
    """
    API Get User's pending contacts
    """
    try:
        pending_contacts = user_service.get_pending_contacts(id)
        return DataResponse().success_response(data=pending_contacts)
    except Exception:
        raise UserError.CANNOT_GET_USER_PENDING_CONTACTS.as_http_exception()

@router.post(
    "/{user_id}/contacts/{friend_id}",
    dependencies=[Depends(login_required)],
    response_model=DataResponse[FriendSchemaResponse],
)
def add_contact(user_id: int, friend_id: int, user_service: UserService = Depends()) -> Any:
    """
    API Add contact
    """
    try:
        contact = user_service.create_friend_request(user_id, friend_id)
        return DataResponse().success_response(data=contact)
    except Exception:
        raise UserError.CANNOT_ADD_CONTACT.as_http_exception()


@router.get(
    "/{id}/groups",
    dependencies=[Depends(login_required)],
    response_model=DataResponse[list[Any]],
)
def get_user_groups(id: int, user_service: UserService = Depends()) -> Any:
    """
    API Get User's groups
    """
    try:
        groups = user_service.get_groups(id)
        return DataResponse().success_response(data=groups)
    except Exception:
        raise UserError.CANNOT_GET_USER_GROUPS.as_http_exception()


@router.post(
    "/groups",
    dependencies=[Depends(PermissionRequired("admin"))],
    response_model=DataResponse[Any],
)
def create_group(group_data: Any, user_service: UserService = Depends()) -> Any:
    """
    API Create new group
    """
    try:
        new_group = user_service.create_group(group_data)
        return DataResponse().success_response(data=new_group)
    except Exception:
        raise UserError.CANNOT_CREATE_GROUP.as_http_exception()


@router.get(
    "/groups/{id}",
    dependencies=[Depends(login_required)],
    response_model=DataResponse[Any],
)
def get_group(id: int, user_service: UserService = Depends()) -> Any:
    """
    API Get group information
    """
    try:
        group = user_service.get_group(id)
        return DataResponse().success_response(data=group)
    except Exception:
        raise UserError.CANNOT_GET_GROUP_DETAIL.as_http_exception()


@router.put(
    "/groups/{id}",
    dependencies=[Depends(PermissionRequired("admin"))],
    response_model=DataResponse[Any],
)
def update_group(
    id: int, group_data: Any, user_service: UserService = Depends()
) -> Any:
    """
    API Update group information
    """
    try:
        updated_group = user_service.update_group(id, group_data)
        return DataResponse().success_response(data=updated_group)
    except Exception:
        raise UserError.CANNOT_UPDATE_GROUP.as_http_exception()


@router.post(
    "/groups/{id}/members",
    dependencies=[Depends(PermissionRequired("admin"))],
    response_model=DataResponse[Any],
)
def add_group_member(
    id: int, user_id: int, user_service: UserService = Depends()
) -> Any:
    """
    API Add member to group
    """
    try:
        member = user_service.add_group_member(id, user_id)
        return DataResponse().success_response(data=member)
    except Exception:
        raise UserError.CANNOT_ADD_GROUP_MEMBER.as_http_exception()


@router.delete(
    "/groups/{id}/members/{user_id}",
    dependencies=[Depends(PermissionRequired("admin"))],
    response_model=DataResponse[Any],
)
def remove_group_member(
    id: int, user_id: int, user_service: UserService = Depends()
) -> Any:
    """
    API Remove member from group
    """
    try:
        user_service.remove_group_member(id, user_id)
        return DataResponse().success_response(data=None)
    except Exception:
        raise UserError.CANNOT_REMOVE_GROUP_MEMBER.as_http_exception()
