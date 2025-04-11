import logging
from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, Query
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
from app.schemas.sche_friend import FriendsListResponse, FriendSchemaResponse
from app.services.srv_user import UserService
from app.services.srv_friend import FriendService
from app.models import User
from app.services.srv_user import UserService
from app.exception.user_error import UserError

logger = logging.getLogger()
router = APIRouter()


@router.get(
    "/me",
    response_model=DataResponse[UserDetailItemResponse],
)
def get_me(
    user: User = Depends(login_required), user_service: UserService = Depends()
) -> Any:
    """
    API Get User information
    """
    try:
        return DataResponse().success_response(
            data=user_service.get_detail(int(user.id))
        )
    except Exception:
        raise UserError.CANNOT_GET_USER.as_http_exception()


@router.get(
    "/{id}",
    dependencies=[Depends(login_required)],
    response_model=DataResponse[UserItemResponse],
)
def get(id: int, user_service: UserService = Depends()) -> Any:
    """
    API Get User information
    """
    try:
        return DataResponse().success_response(data=user_service.get(id))
    except Exception:
        raise UserError.CANNOT_GET_USER_DETAIL.as_http_exception()


@router.put(
    "/me",
    response_model=DataResponse[UserItemResponse],
)
def update_user(
    user_data: UserUpdateRequest,
    user: User = Depends(login_required),
    user_service: UserService = Depends(),
) -> Any:
    """
    API Update User information
    """
    try:
        updated_user = user_service.update(user_id=int(user.id), data=user_data)
        return DataResponse().success_response(data=updated_user)
    except Exception:
        raise UserError.CANNOT_UPDATE_USER_ACCOUNT.as_http_exception()


@router.get(
    "/",
    dependencies=[Depends(login_required)],
    response_model=DataResponse[List[UserItemResponse]],
)
def search_users(
    text: str = Query(..., description="Search by full name or phone number"),
    user_service: UserService = Depends(),
):
    """
    Search users by full name or phone number.
    """
    results = user_service.search_user(text)
    return DataResponse().success_response(data=results)


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
def add_contact(
    user_id: int, friend_id: int, user_service: UserService = Depends()
) -> Any:
    """
    API Add contact
    """
    try:
        contact = user_service.create_friend_request(user_id, friend_id)
        return DataResponse().success_response(data=contact)
    except Exception:
        raise UserError.CANNOT_ADD_CONTACT.as_http_exception()
