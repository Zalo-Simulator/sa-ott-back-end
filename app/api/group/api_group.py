from typing import Any

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.group.schema_group import CreateNewGroupRequest, CreateNewGroupResponse
from app.db.base import get_db
from app.exception.zalo_error import ZaloError
from app.helpers.login_manager import login_required
from app.models import User
from app.models.model_group import Group, GroupMember
from app.schemas.sche_base import DataResponse

router = APIRouter()


@router.post("/", response_model=DataResponse[CreateNewGroupResponse])
def create_new_group(
    payload: CreateNewGroupRequest,
    user: User = Depends(login_required),
    db: Session = Depends(get_db),
) -> Any:
    try:
        group = Group(
            name=payload.name,
            created_by=user.id,
            type=payload.type,
            visible=False if payload.type == "private" else True,
        )
        db.add(group)
        db.commit()
        db.refresh(group)

        # Add group members
        group_member = GroupMember(
            group_id=group.id,
            user_id=user.id,
            role="admin",
        )
        db.add(group_member)
        db.commit()
        db.refresh(group_member)

        # Add other members
        for member_id in payload.member_ids:
            if member_id == user.id:
                continue
            group_member = GroupMember(
                group_id=group.id,
                user_id=member_id,
                role="member",
            )
            db.add(group_member)
            db.commit()
            db.refresh(group_member)
        return DataResponse().success_response(data=CreateNewGroupResponse())
    except Exception as e:
        print("Error creating group:", e)
        raise ZaloError.CANNOT_UPLOAD_FILE.as_http_exception()
