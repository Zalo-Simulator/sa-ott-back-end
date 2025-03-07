from fastapi_sqlalchemy import db

from app.models.model_friend import Friend

from app.schemas.sche_friend import (
    FriendSchemaResponse, 
    CreateFriendRequest,
    UpdateFriendRequest
    )

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

        return [FriendSchemaResponse(**friend.__dict__) for friend in friends]
    
    @staticmethod
    def get_pending_friends(user_id):
        friends = db.session.query(Friend).filter(
            (Friend.user_id == user_id) | (Friend.friend_id == user_id),
            Friend.status == 'pending'
        ).all()

        return [FriendSchemaResponse(**friend.__dict__) for friend in friends]
    
    @staticmethod
    def create_friend_request(params: CreateFriendRequest):
        new_friend_request = Friend(
            user_id=params.user_id,
            friend_id=params.friend_id,
            status=params.status,
            friend_nick_name=params.friend_nick_name
        )
        db.session.add(new_friend_request)
        db.session.commit()
        return new_friend_request

    @staticmethod
    def update_friend_request(friend_id: int, params: UpdateFriendRequest):
        current_friend = db.session.query(Friend).get(friend_id)
        if current_friend.status == "pending" and params.status == "accepted":
            new_friend = Friend(
                user_id=params.friend_id,
                friend_id=params.user_id,
                status="accepted",
                riend_nick_name=params.friend_nick_name
            )
            db.session.add(new_friend)
            current_friend.status = "accepted"
            db.session.commit()
            return current_friend
        
        