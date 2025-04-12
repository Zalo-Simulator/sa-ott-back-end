from typing import Any
from datetime import datetime
import logging

from fastapi import APIRouter, HTTPException, Depends
from fastapi_sqlalchemy import db
from pydantic import EmailStr, BaseModel

from app.core.security import create_access_token, verify_password
from app.schemas.sche_base import DataResponse
from app.schemas.sche_token import Token, LoginResponse, ChangePassword, ResetPassword
from app.services.srv_user import UserService
from app.exception.auth_error import AuthenticationError
from app.schemas.sche_user import UserItemResponse, UserRegisterRequest

logger = logging.getLogger()
router = APIRouter()
auth_router = APIRouter()


class LoginRequest(BaseModel):
    phone: str = "0975828593"
    password: str = "secret123"


@router.post("/login", response_model=DataResponse[LoginResponse])
def login_access_token(form_data: LoginRequest, user_service: UserService = Depends()):
    try:
        user = user_service.authenticate(
            phone=form_data.phone, password=form_data.password
        )
    except HTTPException as e:
        raise e
    if not user.is_active:
        raise AuthenticationError.INACTIVE_USER.as_http_exception()

    setattr(user, "last_login", datetime.now())
    user.is_online = True
    db.session.commit()

    return DataResponse().success_response({
        "id": user.id,
        "full_name": user.full_name,
        "avatar_url": user.avatar_url,
        "access_token": create_access_token(user_id=user.id),
        "token_type": "bearer",
    })


@auth_router.post("/register", response_model=DataResponse[UserItemResponse])
def auth_register(
    register_data: UserRegisterRequest, user_service: UserService = Depends()
) -> Any:
    try:
        register_user = user_service.register_user(register_data)
        return DataResponse().success_response(data=register_user)
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.exception("REGISTER ERROR: %s", e)
        raise AuthenticationError.CANNOT_REGISTER_ACCOUNT.as_http_exception()


@router.post("/logout", response_model=DataResponse[None])
def auth_logout(current_user=Depends(UserService.get_current_user)):
    """logout api"""
    current_user.is_online = False
    return DataResponse().success_response(data=None)


@router.post("/refresh-token", response_model=DataResponse[Token])
def auth_refresh_token(current_user=Depends(UserService.get_current_user)):
    """refresh-token api"""
    new_token = create_access_token(user_id=current_user.id)
    return DataResponse().success_response({
        "access_token": new_token,
        "token_type": "bearer",
    })


@router.put("/change-password", response_model=DataResponse[None])
def auth_change_password(
    form_data: ChangePassword,
    current_user=Depends(UserService.get_current_user),
    user_service: UserService = Depends(),
):
    if not verify_password(form_data.current_password, current_user.password_hash):
        raise AuthenticationError.INVALID_USER_LOGIN.as_http_exception()

    user_service.change_password(
        user_id=current_user.id, new_password=form_data.new_password
    )

    return DataResponse().success_response(data=None)


@router.post("/reset-password", response_model=DataResponse[None])
def auth_reset_password(
    form_data: ResetPassword, user_service: UserService = Depends()
):
    user_service.reset_password(phone=form_data.phone, new_password=form_data.password)
    return DataResponse().success_response(data=None)
