import logging

import requests
from fastapi_sqlalchemy import db

from app.models.model_friend import Friend
from app.api.constants import USER_API_URL
from app.schemas.sche_friend import (
    FriendSchemaResponse,
    CreateFriendRequest,
    UpdateFriendRequest
)
from app.exception.friend_error import FriendError

logger = logging.getLogger()


class FriendService(object):
    __instance = None

    def __init__(self) -> None:
        pass

    @staticmethod
    def get_friends(user_id):
        friends = db.session.query(Friend).filter(
            (Friend.user_id == user_id) | (Friend.friend_id == user_id),
            Friend.status == 'accepted'
        ).all()
        if friends is None:
            raise FriendError.CANNOT_GET_FRIEND_LIST.as_http_exception()
        return [FriendSchemaResponse(**friend.__dict__) for friend in friends]

    @staticmethod
    def get_pending_friends(user_id):
        friends = db.session.query(Friend).filter(
            (Friend.user_id == user_id) | (Friend.friend_id == user_id),
            Friend.status == 'pending'
        ).all()
        if friends is None:
            raise FriendError.CANNOT_GET_FRIEND_LIST.as_http_exception()
        return [FriendSchemaResponse(
            id = friend.id,
            user_id=friend.user_id,
            friend_id=friend.friend_id,
            status=friend.status,
            friend_nick_name=friend.friend_nick_name) for friend in friends]

    @staticmethod
    def create_friend_request(params: CreateFriendRequest):
        exist_friend = db.session.query(Friend).filter(
            (Friend.user_id == params.user_id) & (Friend.friend_id == params.friend_id)).first()
        if exist_friend is not None:
            logger.error("Friend request existed")
            raise FriendError.FRIEND_REQUEST_EXISTED.as_http_exception()
        if params.friend_nick_name is None:
            response = requests.get(USER_API_URL + f"/{params.friend_id}")
            if response.status_code == 200:
                params.friend_nick_name = response.json().get("data").get("full_name")
            else:
                raise FriendError.USER_NOT_FOUND.as_http_exception()
        new_friend_request = Friend(
            user_id=params.user_id,
            friend_id=params.friend_id,
            status=params.status,
            friend_nick_name=params.friend_nick_name
        )
        db.session.add(new_friend_request)
        db.session.commit()
        return FriendSchemaResponse(
            id=new_friend_request.id,
            user_id=new_friend_request.user_id,
            friend_id=new_friend_request.friend_id,
            status=new_friend_request.status,
            friend_nick_name=new_friend_request.friend_nick_name
        )

    @staticmethod
    def update_friend_request(friend_id: int, params: UpdateFriendRequest):
        current_friend  = db.session.query(Friend).filter_by(id=friend_id).first()
        if current_friend is None:
            raise FriendError.CANNOT_GET_FRIEND_LIST.as_http_exception()
        current_friend.user_id = params.user_id if params.user_id else current_friend.user_id
        current_friend.friend_id = params.friend_id if params.friend_id else current_friend.friend_id
        current_friend.status = params.status if params.status else current_friend.status
        current_friend.friend_nick_name = params.friend_nick_name if params.friend_nick_name else current_friend.friend_nick_name
        db.session.commit()
        return current_friend


    @staticmethod
    def delete_friend_request(friend_id: int):
        current_friend = db.session.query(Friend).get(friend_id)
        if current_friend is None:
            raise FriendError.CANNOT_GET_FRIEND_LIST.as_http_exception()
        db.session.delete(current_friend)
        db.session.commit()
        return current_friend
