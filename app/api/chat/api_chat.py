from typing import Any, List

from fastapi import APIRouter, Query

from app.api.chat.schema_chat import (
    GetChatGroupResponse,
    PostMessageReactionResponse,
    GetChatGroupRequest,
    MessageDetailSchema,
    MessageDetailPersonSchema,
    MessageDetailReactionModel,
)
from app.exception.zalo_error import ZaloError
from app.schemas.sche_base import DataResponse
from typing import Any
from app.models.model_message import MessageModel
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.models import User
from app.db.base import get_db
from app.helpers.login_manager import login_required
from app.models.model_group import Group, GroupMember

router = APIRouter()


@router.get(
    "/chat/{group_id}",
    response_model=DataResponse[List[MessageDetailSchema]],
    description="Lấy danh sách tin nhắn trong nhóm",
)
def get_chat_group(
    group_id: int,
    limit: int = Query(25, gt=0, le=100),  # Mặc định 100, giới hạn 0 < limit ≤ 1000
    db: Session = Depends(get_db),
    user: User = Depends(login_required),
) -> Any:
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

    return DataResponse().success_response(
        data=[
            MessageDetailSchema(
                person=MessageDetailPersonSchema(
                    id=message.sender_id,
                    full_name=message.sender.full_name,
                    avatar_url=message.sender.avatar_url,
                ),
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
    )


@router.post(
    "/chat/{message_id}/reaction",
    response_model=DataResponse[PostMessageReactionResponse],
)
def post_message_reaction(
    user_id: int,
    message_id: int,
) -> Any:
    pass
