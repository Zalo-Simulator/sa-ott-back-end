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
from app.services.srv_chat import ChatService

router = APIRouter()


@router.get(
    "/chat/{group_id}",
    response_model=DataResponse[List[MessageDetailSchema]],
    description="Lấy danh sách tin nhắn trong nhóm",
)
def get_chat_group(
    group_id: int,
    chat_service: ChatService = Depends(ChatService),
    limit: int = Query(25, gt=0, le=100),  # Mặc định 100, giới hạn 0 < limit ≤ 1000
    db: Session = Depends(get_db),
    user: User = Depends(login_required),
) -> Any:
    try:
        res = chat_service.get_chat_group(
            group_id=group_id,
            db=db,
            user=user,
            limit=limit,
        )
        return DataResponse().success_response(data=res)
    except:
        raise ZaloError.GROUP_NOT_FOUND.as_http_exception()


@router.post(
    "/chat/{message_id}/reaction",
    response_model=DataResponse[PostMessageReactionResponse],
)
def post_message_reaction(
    user_id: int,
    message_id: int,
) -> Any:
    pass
