import logging

from fastapi.security import HTTPBearer
from sqlalchemy.orm.session import Session

from app.api.group.schema_group import (
    CreateNewGroupRequest,
)
from app.exception.zalo_error import ZaloError
from app.models import User
from app.models.model_group import Group, GroupMember

logger = logging.getLogger()

reusable_oauth2 = HTTPBearer(scheme_name="Authorization")


class GroupService(object):
    __instance = None

    def __init__(self) -> None:
        pass

    @staticmethod
    def create_group(user: User, payload: CreateNewGroupRequest, db: Session):
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
        except Exception:
            db.rollback()
            raise ZaloError.CANNOT_CREATE_GROUP.as_http_exception()
        try:
            # Add group members
            group_member = GroupMember(
                group_id=group.id,
                user_id=user.id,
                role="admin",
            )
            db.add(group_member)
            db.commit()
            db.refresh(group_member)
        except Exception:
            db.rollback()
            raise ZaloError.CANNOT_ACCESS_ADMIN_GROUP.as_http_exception()

        try:
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
            return group
        except Exception as e:
            logger.error("Error creating group: %s", str(e))
            db.rollback()
            raise ZaloError.CANNOT_ADD_MEMBER.as_http_exception()
