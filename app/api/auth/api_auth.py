from typing import Any
from datetime import datetime

from fastapi import APIRouter, HTTPException, Depends
from fastapi_sqlalchemy import db
from pydantic import EmailStr, BaseModel

from app.core.security import create_access_token
from app.schemas.sche_base import DataResponse
from app.schemas.sche_token import Token
from app.services.srv_user import UserService
from app.exception.auth_error import AuthenticationError
from app.schemas.sche_user import UserItemResponse, UserRegisterRequest


router = APIRouter()


class LoginRequest(BaseModel):
    username: EmailStr = "tintra17@gmail.com"
    password: str = "secret123"


@router.post("/login", response_model=DataResponse[Token])
def login_access_token(form_data: LoginRequest, user_service: UserService = Depends()):
    user = user_service.authenticate(
        email=form_data.username, password=form_data.password
    )
    if not user:
        raise AuthenticationError.INVALID_USER_LOGIN.as_http_exception()
    elif not user.is_active:
        raise AuthenticationError.INACTIVE_USER.as_http_exception()

    user.last_login = datetime.now()
    db.session.commit()

    return DataResponse().success_response({
        "access_token": create_access_token(user_id=user.id)
    })


@router.post("/register", response_model=DataResponse[UserItemResponse])
def auth_register(
    register_data: UserRegisterRequest, user_service: UserService = Depends()
) -> Any:
    try:
        register_user = user_service.register_user(register_data)
        return DataResponse().success_response(data=register_user)
    except Exception:
        raise AuthenticationError.CANNOT_REGISTER_ACCOUNT.as_http_exception()


@router.post("/logout", response_model=DataResponse[Token])
def auth_logout(form_data: LoginRequest, user_service: UserService = Depends()):
    """logout api"""
    # Implement logout logic here
    return DataResponse().success_response({"message": "Logged out successfully"})


@router.post("/refresh-token", response_model=DataResponse[Token])
def auth_refresh_token(form_data: LoginRequest, user_service: UserService = Depends()):
    """refresh-token api"""
    # Implement refresh token logic here
    new_token = create_access_token(user_id=form_data.username)
    return DataResponse().success_response({"access_token": new_token})


@router.put("/change-password", response_model=DataResponse[Token])
def auth_change_password(
    form_data: LoginRequest, user_service: UserService = Depends()
):
    """change password api"""
    # Implement change password logic here
    user_service.change_password(
        email=form_data.username, new_password=form_data.password
    )
    return DataResponse().success_response({"message": "Password changed successfully"})


@router.post("/reset-password", response_model=DataResponse[Token])
def auth_reset_password(form_data: LoginRequest, user_service: UserService = Depends()):
    """reset-password api"""
    # Implement reset password logic here
    user_service.reset_password(email=form_data.username)
    return DataResponse().success_response({"message": "Password reset successfully"})
