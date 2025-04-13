from typing import Any, List

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm.session import Session

from app.schemas.sche_chat import (
    MessageDetailPersonSchema,
    MessageDetailReactionModel,
    MessageDetailSchema,
    PostMessageReactionResponse,
)
from app.db.base import get_db
from app.exception.zalo_error import ZaloError
from app.helpers.login_manager import login_required
from app.models import User
from app.models.model_group import GroupMember
from app.models.model_message import MessageModel
from app.schemas.sche_base import DataResponse


class ChatService(object):
    __instance = None

    def __init__(self) -> None:
        pass

    def get_chat_group(
        group_id: int,
        db: Session,
        user: User,
        # Mặc định 100, giới hạn 0 < limit ≤ 1000
        limit: int = Query(25, gt=0, le=100),
    ):
        db_group = (
            db.query(GroupMember)
            .filter((GroupMember.group_id == group_id) & (GroupMember.user_id == user.id))
            .first()
        )
        if db_group is None:
            raise ZaloError.GROUP_NOT_FOUND.as_http_exception()

        db_group_messages: List[MessageModel] = (
            db.query(MessageModel)
            .filter(MessageModel.group_id == group_id)
            .order_by(MessageModel.created_at.desc())
            .limit(limit)
            .all()
        )

        return [MessageDetailSchema(
                    person=MessageDetailPersonSchema(
                        id=message.sender_id,
                        full_name=message.sender.full_name,
                        avatar_url=message.sender.avatar_url,
                    ),
                    message_id=message.id,
                    message=message.content,
                    message_type=message.message_type,
                    attachment_id=[],  # TODO future
                    time=message.created_at,
                    reactions=[
                        MessageDetailReactionModel(
                            id=reaction.id,
                            full_name=reaction.sender.full_name,
                            avatar_url=reaction.sender.avatar_url,
                            reaction=reaction.reaction,
                            count=reaction.count,
                        )
                        for reaction in message.reactions
                    ],
                )
                for message in db_group_messages
            ]
        