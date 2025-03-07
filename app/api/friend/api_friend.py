import logging
from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException
from fastapi_sqlalchemy import db

from app.exception.friend_error import FriendError
from app.helpers.login_manager import login_required, PermissionRequired
from app.helpers.paging import Page, PaginationParams, paginate
from app.schemas.sche_base import DataResponse
from app.schemas.sche_friend import (
    FriendSchemaResponse,
    CreateFriendRequest
)
from app.services.srv_friend import FriendService
from app.models import Friend

logger = logging.getLogger()
router = APIRouter()

@router.get(
    "/{id}",
    dependencies=[Depends(login_required)],
    response_model=DataResponse[FriendSchemaResponse],
)
def get(
    user_id: int,
    friend_service: FriendService = Depends()
) -> List[FriendSchemaResponse]:
    """
    API Get Friend information
    """
    try:
        return DataResponse().success_response(data=friend_service.get_friends(user_id))
    except Exception:
        raise FriendError.CANNOT_GET_FRIEND_DETAIL.as_http_exception()

@router.get(
    "/{user_id}/pending",
    dependencies=[Depends(login_required)],
    response_model=DataResponse[List[FriendSchemaResponse]],
)
def get_pending(
    user_id: int,
    friend_service: FriendService = Depends()
):
    """
    API Get Pending Friend information
    """
    try:
        return DataResponse().success_response(data=friend_service.get_pending_friends(user_id))
    except Exception:
        raise FriendError.CANNOT_GET_FRIEND_DETAIL.as_http_exception()
    
@router.post(
    "/",
    dependencies=[Depends(login_required)],
    response_model=DataResponse[Any],
)
def create(
    params: CreateFriendRequest,
    friend_service: FriendService = Depends()
) -> Any:
    """
    API Create Friend information
    """
    try:
        return DataResponse().success_response(data=friend_service.create_friend_request(params))
    except FriendError as e: 
        if e == FriendError.FRIEND_REQUEST_EXISTED:
            logger.error("Friend request existed")
            raise e.as_http_exception()  
        raise e.as_http_exception()
    
@router.put(
    "/{id}",
    dependencies=[Depends(login_required)],
    response_model=DataResponse[FriendSchemaResponse],
)
def update(
    friend_id: int,
    params: CreateFriendRequest,
    friend_service: FriendService = Depends()
) -> Any:
    """
    API Update Friend information
    """
    try:
        return DataResponse().success_response(data=friend_service.update_friend_request(friend_id, params))
    except Exception:
        raise FriendError.CANNOT_UPDATE_FRIEND_REQUEST.as_http_exception()

@router.delete(
    "/{id}",
    dependencies=[Depends(login_required)],
    response_model=DataResponse[FriendSchemaResponse],
)
def delete(
    friend_id: int,
    friend_service: FriendService = Depends()
) -> Any:
    """
    API Delete Friend information
    """
    try:
        return DataResponse().success_response(data=friend_service.delete_friend_request(friend_id))
    except Exception:
        raise FriendError.CANNOT_DELETE_FRIEND_REQUEST.as_http_exception()