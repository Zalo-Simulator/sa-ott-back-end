import logging
from typing import Any

from fastapi import APIRouter, Depends

from app.exception.user_error import UserError
from app.helpers.login_manager import login_required
from app.models import User
from app.schemas.sche_base import DataResponse
from app.schemas.sche_friend import FriendSchemaResponse, FriendsListResponse
from app.services.srv_user import UserService

logger = logging.getLogger()
router = APIRouter()


@router.get(
    "/",
    dependencies=[Depends(login_required)],
    response_model=DataResponse[FriendsListResponse],
)
def get_user_contacts(
    user: User = Depends(login_required), user_service: UserService = Depends()
) -> Any:
    """
    API Get User's contacts
    """
    try:
        contacts = user_service.get_contacts(user.id)
        return DataResponse().success_response(data=contacts)
    except Exception:
        raise UserError.CANNOT_GET_USER_CONTACTS.as_http_exception()


@router.get(
    "/pending",
    dependencies=[Depends(login_required)],
    response_model=DataResponse[FriendsListResponse],
)
def get_user_pending_contacts(
    user: User = Depends(login_required), user_service: UserService = Depends()
) -> Any:
    """
    API Get User's pending contacts
    """
    try:
        pending_contacts = user_service.get_pending_contacts(user.id)
        return DataResponse().success_response(data=pending_contacts)
    except Exception:
        raise UserError.CANNOT_GET_USER_PENDING_CONTACTS.as_http_exception()


@router.post(
    "/{friend_id}",
    dependencies=[Depends(login_required)],
    response_model=DataResponse[FriendSchemaResponse],
)
def add_contact(
    friend_id: int,
    user: User = Depends(login_required),
    user_service: UserService = Depends(),
) -> Any:
    """
    API Add contact
    """
    try:
        contact = user_service.create_friend_request(user.id, friend_id)
        return DataResponse().success_response(data=contact)
    except Exception:
        raise UserError.CANNOT_ADD_CONTACT.as_http_exception()


@router.put(
    "/{friend_id}",
    dependencies=[Depends(login_required)],
)
def update_friend(
    friend_id: int,
    user: User = Depends(login_required),
    user_service: UserService = Depends(),
) -> Any:
    try:
        contact = user_service.update_friend_request(int(user.id), friend_id)
        return DataResponse().success_response(data=contact)
    except Exception:
        raise UserError.CANNOT_ADD_CONTACT.as_http_exception()


@router.delete(
    "/{friend_id}",
    dependencies=[Depends(login_required)],
)
def delete_friend(
    friend_id: int,
    user: User = Depends(login_required),
    user_service: UserService = Depends(),
) -> Any:
    """
    API Add contact
    """
    try:
        contact = user_service.delete_friend(user.id, friend_id)
        return DataResponse().success_response(data=contact)
    except Exception:
        raise UserError.CANNOT_ADD_CONTACT.as_http_exception()
