from typing import Any

from fastapi import APIRouter, Query

from app.api.chat.schema_chat import GetChatGroupResponse, PostMessageReactionResponse
from app.exception.zalo_error import ZaloError
from app.schemas.sche_base import DataResponse

router = APIRouter()


@router.get("/chat/{group_id}", response_model=DataResponse[GetChatGroupResponse])
def get_chat_group(
    user_id: int,
    group_id: int,
    limit: int = Query(100, gt=0, le=1000),  # Mặc định 100, giới hạn 0 < limit ≤ 1000
) -> Any:
    try:
        pass
    except Exception:
        raise ZaloError.CANNOT_UPLOAD_FILE.as_http_exception()


@router.post(
    "/chat/{message_id}/reaction",
    response_model=DataResponse[PostMessageReactionResponse],
)
def post_message_reaction(
    user_id: int,
    message_id: int,
) -> Any:
    pass
