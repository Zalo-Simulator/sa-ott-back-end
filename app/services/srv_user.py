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
    UserDetailItemResponse,
)
from app.models.model_friend import Friend
from app.api.constants import USER_API_URL
from app.schemas.sche_friend import (
    FriendSchemaResponse,
    FriendsListResponse,
    CreateFriendRequest,
    UpdateFriendRequest,
)
from app.exception.friend_error import FriendError

logger = logging.getLogger()

reusable_oauth2 = HTTPBearer(scheme_name="Authorization")


class UserService(object):
    __instance = None

    def __init__(self) -> None:
        pass

    @staticmethod
    def authenticate(*, phone: str, password: str) -> Optional[User]:
        """
        Check username and password is correct.
        Return object User if correct, else return None
        """
        user = db.session.query(User).filter(User.phone == phone).first()
        if not user:
            return "User not found"
        if not verify_password(password, user.password_hash):
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
        exist_user_by_phone = (
            db.session.query(User).filter(User.phone == data.phone).first()
        )
        if exist_user_by_phone:
            raise AuthenticationError.PHONE_ALREADY_EXIST.as_http_exception()

        register_user = User(
            phone=data.phone,
            full_name=data.full_name,
            password_hash=get_password_hash(data.password),
            is_active=True,
            status="Available",
        )
        db.session.add(register_user)
        db.session.commit()

        return UserItemResponse(
            id=register_user.id,
            full_name=register_user.full_name,
            is_active=register_user.is_active,
        )

    @staticmethod
    def create_user(data: UserCreateRequest):
        exist_user = db.session.query(User).filter(User.phone == data.phone).first()
        if exist_user:
            raise AuthenticationError.PHONE_ALREADY_EXIST.as_http_exception()
        new_user = User(
            phone=data.phone,
            full_name=data.full_name,
            hashed_password=get_password_hash(data.password),
            is_active=data.is_active,
        )
        db.session.add(new_user)
        db.session.commit()
        return new_user

    @staticmethod
    def update(user_id: int, data: UserUpdateRequest):
        user = db.session.query(User).get(user_id)
        if user is None:
            raise AuthenticationError.USER_NOT_FOUND.as_http_exception()
        user.full_name = user.full_name if data.full_name is None else data.full_name
        user.is_active = user.is_active if data.is_active is None else data.is_active
        user.avatar_url = user.avatar_url if data.avatar_url is None else data.avatar_url

        db.session.commit()
        return user
    
    @staticmethod
    def change_password(user_id: int, new_password: str):
        user = db.session.query(User).get(user_id)
        if not user:
            raise AuthenticationError.USER_NOT_FOUND.as_http_exception()

        user.password_hash = get_password_hash(new_password)
        db.session.commit()

    @staticmethod
    def reset_password(phone: str, new_password: str):
        user = db.session.query(User).filter(User.phone == phone).first()
        if not user:
            raise AuthenticationError.USER_NOT_FOUND.as_http_exception()

        user.password_hash = get_password_hash(new_password)
        db.session.commit()


    @staticmethod
    def get_detail(user_id):
        exist_user = db.session.query(User).get(user_id)
        if exist_user is None:
            raise AuthenticationError.USER_NOT_FOUND.as_http_exception()
        return exist_user

    @staticmethod
    def get(user_id: int):
        exist_user: User = db.session.query(User).get(user_id)
        if exist_user is None:
            raise AuthenticationError.USER_NOT_FOUND.as_http_exception()
        return UserItemResponse(
            id=exist_user.id,
            avatar_url=exist_user.avatar_url,
            full_name=exist_user.full_name,
            is_active=exist_user.is_active,
        )

    @staticmethod
    def get_contacts(user_id):
        friends = (
            db.session.query(Friend)
            .filter(
                (Friend.user_id == user_id) | (Friend.friend_id == user_id),
                Friend.status == "accepted",
            )
            .all()
        )
        if friends is None:
            raise FriendError.CANNOT_GET_FRIEND_LIST.as_http_exception()
        user_id = [friend.user_id for friend in friends if friend.user_id != user_id]
        user_id += [
            friend.friend_id for friend in friends if friend.friend_id != user_id
        ]
        user_id = list(set(user_id))
        contacts = db.session.query(User).filter(User.id.in_(user_id)).all()
        if contacts is None:
            raise AuthenticationError.USER_NOT_FOUND.as_http_exception()

        return FriendsListResponse(
            friends=[
                UserItemResponse(
                    id=contact.id,
                    full_name=contact.full_name,
                    avatar_url=contact.avatar_url,
                    is_active=contact.is_active,
                )
                for contact in contacts
            ]
        )

    @staticmethod
    def create_friend_request(user_id: int, friend_id: int):
        exist_friend = (
            db.session.query(Friend)
            .filter((Friend.user_id == user_id) & (Friend.friend_id == friend_id))
            .first()
        )
        if exist_friend is not None:
            logger.error("Friend request existed")
            raise FriendError.FRIEND_REQUEST_EXISTED.as_http_exception()
        friend = UserService.get(friend_id)
        if friend is None:
            raise FriendError.USER_NOT_FOUND.as_http_exception()
        friend_nick_name = friend.full_name
        new_friend_request = Friend(
            user_id=user_id,
            friend_id=friend_id,
            status="pending",
            friend_nick_name=friend_nick_name,
        )
        db.session.add(new_friend_request)
        db.session.commit()
        return FriendSchemaResponse(
            id=new_friend_request.id,
            user_id=new_friend_request.user_id,
            friend_id=new_friend_request.friend_id,
            status=new_friend_request.status,
            friend_nick_name=new_friend_request.friend_nick_name,
        )

    @staticmethod
    def get_pending_contacts(user_id: int):
        friends = (
            db.session.query(Friend)
            .filter((Friend.friend_id == user_id), Friend.status == "pending")
            .all()
        )
        if friends is None:
            raise FriendError.CANNOT_GET_FRIEND_LIST.as_http_exception()
        friend_id = [friend.user_id for friend in friends]
        friend_id = list(set(friend_id))
        contacts = db.session.query(User).filter(User.id.in_(friend_id)).all()
        if contacts is None:
            raise AuthenticationError.USER_NOT_FOUND.as_http_exception()
        return FriendsListResponse(
            friends=[
                UserItemResponse(
                    id=contact.id,
                    full_name=contact.full_name,
                    avatar_url=contact.avatar_url,
                    is_active=contact.is_active,
                )
                for contact in contacts
            ]
        )

    def update_friend_request(friend_id: int, params: UpdateFriendRequest):
        current_friend = db.session.query(Friend).filter_by(id=friend_id).first()
        if current_friend is None:
            raise FriendError.CANNOT_GET_FRIEND_LIST.as_http_exception()
        current_friend.user_id = (
            params.user_id if params.user_id else current_friend.user_id
        )
        current_friend.friend_id = (
            params.friend_id if params.friend_id else current_friend.friend_id
        )
        current_friend.status = (
            params.status if params.status else current_friend.status
        )
        current_friend.friend_nick_name = (
            params.friend_nick_name
            if params.friend_nick_name
            else current_friend.friend_nick_name
        )
        db.session.commit()
        return current_friend
