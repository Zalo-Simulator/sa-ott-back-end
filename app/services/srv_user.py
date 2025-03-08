import jwt
import logging

from typing import Optional
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer
from fastapi_sqlalchemy import db
from pydantic import ValidationError
from starlette import status
from app.exception.auth_error import AuthenticationError
from app.models import User
from app.core.config import settings
from app.core.security import verify_password, get_password_hash
from app.schemas.sche_token import TokenPayload
from app.schemas.sche_user import (
    UserItemResponse,
    UserCreateRequest,
    UserUpdateMeRequest,
    UserUpdateRequest,
    UserRegisterRequest,
)

logger = logging.getLogger()
class UserService(object):
    __instance = None

    def __init__(self) -> None:
        pass

    reusable_oauth2 = HTTPBearer(scheme_name="Authorization")

    @staticmethod
    def authenticate(*, phone: str, password: str) -> Optional[User]:
        """
        Check username and password is correct.
        Return object User if correct, else return None
        """
        user = db.session.query(User).filter(User.phone == phone).first()
        if not user:
            return "User not found"
        if not verify_password(password, user.hashed_password):
            return "Password is incorrect"
        return user

    @staticmethod
    def get_current_user(
        http_authorization_credentials=Depends(reusable_oauth2),
    ) -> User:
        """
        Decode JWT token to get user_id => return User info from DB query
        """
        try:
            payload = jwt.decode(
                http_authorization_credentials.credentials,
                settings.SECRET_KEY,
                algorithms=[settings.SECURITY_ALGORITHM],
            )
            token_data = TokenPayload(**payload)
        except (jwt.PyJWTError, ValidationError):
            raise AuthenticationError.INVALID_CREDENTIALS.as_http_exception()
        user = db.session.query(User).get(token_data.user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user

    @staticmethod
    def register_user(data: UserRegisterRequest):
        exist_user_by_email = db.session.query(User).filter(User.email == data.email).first()
        if exist_user_by_email:
            logger.error(f"Email {data.email} already exists")
            raise AuthenticationError.EMAIL_ALREADY_EXIST.as_http_exception()

        exist_user_by_phone = db.session.query(User).filter(User.phone == data.phone).first()
        if exist_user_by_phone:
            logger.error(f"Phone {data.phone} already exists")  # ✅ Corrected log message
            raise AuthenticationError.PHONE_ALREADY_EXIST.as_http_exception()  # ✅ Use correct error

        register_user = User(
            phone=data.phone,
            full_name=data.full_name,
            email=data.email,
            hashed_password=get_password_hash(data.password),
            is_active=True,
            role=data.role.value,
        )
        db.session.add(register_user)
        db.session.commit()
        return register_user

    @staticmethod
    def create_user(data: UserCreateRequest):
        exist_user = db.session.query(User).filter(User.email == data.email).first()
        if exist_user:
            raise AuthenticationError.EMAIL_ALREADY_EXIST.as_http_exception()
        new_user = User(
            phone=data.phone,
            full_name=data.full_name,
            email=data.email,
            hashed_password=get_password_hash(data.password),
            is_active=data.is_active,
            role=data.role.value,
        )
        db.session.add(new_user)
        db.session.commit()
        return new_user

    @staticmethod
    def update_me(data: UserUpdateMeRequest, current_user: User):
        if data.email is not None:
            exist_user = (
                db.session.query(User)
                .filter(User.email == data.email, User.id != current_user.id)
                .first()
            )
            if exist_user:
                raise AuthenticationError.EMAIL_ALREADY_EXIST.as_http_exception()
        current_user.full_name = (
            current_user.full_name if data.full_name is None else data.full_name
        )
        current_user.email = current_user.email if data.email is None else data.email
        current_user.hashed_password = (
            current_user.hashed_password
            if data.password is None
            else get_password_hash(data.password)
        )
        db.session.commit()
        return current_user

    @staticmethod
    def update(user_id: int, data: UserUpdateRequest):
        user = db.session.query(User).get(user_id)
        if user is None:
            raise AuthenticationError.USER_NOT_FOUND.as_http_exception()
        user.full_name = user.full_name if data.full_name is None else data.full_name
        user.email = user.email if data.email is None else data.email
        user.hashed_password = (
            user.hashed_password
            if data.password is None
            else get_password_hash(data.password)
        )
        user.is_active = user.is_active if data.is_active is None else data.is_active
        user.role = user.role if data.role is None else data.role.value
        db.session.commit()
        return user

    @staticmethod
    def get_detail(user_id):
        exist_user = db.session.query(User).get(user_id)
        if exist_user is None:
            raise AuthenticationError.USER_NOT_FOUND.as_http_exception()
        return exist_user

    @staticmethod
    def get(user_id):
        exist_user = db.session.query(User).get(user_id)
        if exist_user is None:
            raise AuthenticationError.USER_NOT_FOUND.as_http_exception()
        return UserItemResponse(
            id=exist_user.id,
            full_name=exist_user.full_name,
            is_active=exist_user.is_active,
            role=exist_user.role,
        )



