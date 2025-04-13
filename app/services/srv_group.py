import logging

from fastapi.security import HTTPBearer
from sqlalchemy.orm.session import Session

from app.exception.zalo_error import ZaloError
from app.models import User
from app.models.model_group import Group, GroupMember
from app.schemas.sche_group import (
    CreateNewGroupRequest,
    CreateNewGroupResponse,
    GetGroupByGroupIdResponse,
    GetGroupsByUserIdResponse,
    GroupID,
    GroupMemberSimpleResponse,
    GroupMembersResponse,
    GroupsResponse,
    UpdateGroupRequest,
    UpdateGroupResponse,
    UpdateGroupSimpleResponse,
)

logger = logging.getLogger()

reusable_oauth2 = HTTPBearer(scheme_name="Authorization")


class GroupService(object):
    __instance = None

    def __init__(self) -> None:
        pass

    @staticmethod
    def get_group_by_user(user_id: int, page, limit, db: Session):
        db_group_members = (
            db.query(GroupMember)
            .filter(GroupMember.user_id == user_id)
            .limit(limit)
            .offset(page)
            .all()
        )
        return GetGroupsByUserIdResponse(
            groups=[
                GroupsResponse(
                    id=group_member.group_id,
                    name=group_member.group.name,
                    type=group_member.group.type,
                    created_by=group_member.group.created_by,
                    visible=group_member.group.visible,
                    member_count=len(group_member.group.members),
                    avatar_url=group_member.group.avatar_url,
                    members=[
                        GroupMembersResponse(
                            id=member.user_id,
                            name=member.user.full_name,
                            avatar_url=member.user.avatar_url,
                            role=member.role,
                            is_online=member.user.is_online,
                        )
                        for member in group_member.group.members
                    ],
                )
                for group_member in db_group_members
            ]
        )

    @staticmethod
    def get_private(user: User, friend_id, db: Session):
        user_groups = db.query(GroupMember).filter(
            GroupMember.user_id == user.id).all()
        friend_groups = db.query(GroupMember).filter(
            GroupMember.user_id == friend_id).all()

        # Extract group_ids from GroupMember (not the record id!)
        user_group_ids = {group.group_id for group in user_groups}
        friend_group_ids = {group.group_id for group in friend_groups}

        # Find common group IDs
        common_group_ids = user_group_ids.intersection(friend_group_ids)
        if len(common_group_ids) > 0:
            private_group = (
                db.query(Group)
                .filter(
                    Group.id.in_(list(common_group_ids)),
                    Group.type == "private",  # Assuming type is a string field
                )
                .first()
            )

            if private_group is not None:
                return GroupID(id=private_group.id)

        payload = CreateNewGroupRequest(
            name=f"private_group_{str(user.id)}_{str(friend_id)}",
            member_ids=[friend_id],
            type="private",
        )
        try:
            group = GroupService.create_group(user, payload=payload, db=db)
            return GroupID(id=group.id)
        except Exception as e:
            logger.error("Error creating group:%s", e)
            db.rollback()
            raise ZaloError.CANNOT_ADD_MEMBER.as_http_exception()

    @staticmethod
    def get_group_by_group_id(user:User, group_id: int, db: Session):
        db_group = db.query(Group).filter(Group.id == group_id).first()
        if not db_group:
            raise ZaloError.GROUP_NOT_FOUND.as_http_exception()

        if not db_group.visible:  # if it is a private group and user is not a member
            is_member = (
                db.query(GroupMember)
                .filter(GroupMember.group_id == group_id, GroupMember.user_id == user.id)
                .first()
            )
            if not is_member:
                raise ZaloError.GROUP_PERMISSION_DENIED.as_http_exception()

        db_group_members = (
            db.query(GroupMember).filter(
                GroupMember.group_id == group_id).all()
        )

        return GetGroupByGroupIdResponse(
                id=db_group.id,
                name=db_group.name,
                type=db_group.type,
                created_by=db_group.created_by,
                visible=db_group.visible,
                member_count=len(db_group_members),
                avatar_url=db_group.avatar_url,
                members=[
                    GroupMembersResponse(
                        id=member.user_id,
                        name=member.user.full_name,
                        avatar_url=member.user.avatar_url,
                        role=member.role,
                        is_online=member.user.is_online,
                    )
                    for member in db_group_members
                ],
            )
        

    @ staticmethod
    def create_group(user: User, payload: CreateNewGroupRequest, db: Session):
        try:
            group= Group(
                name = payload.name,
                created_by = user.id,
                type = payload.type,
                visible = False if payload.type == "private" else True,
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

    @staticmethod
    def update_group(
        group_id: int,
        payload: UpdateGroupRequest,
        user: User,
        db: Session,
    ) -> UpdateGroupSimpleResponse:
        db_group = db.query(Group).filter(Group.id == group_id).first()
        if not db_group:
            raise ZaloError.GROUP_NOT_FOUND.as_http_exception()

        is_member = (
            db.query(GroupMember)
            .filter(GroupMember.group_id == group_id, GroupMember.user_id == user.id)
            .first()
        )
        if not is_member:
            raise ZaloError.GROUP_PERMISSION_DENIED.as_http_exception()

        if payload.name:
            db_group.name = payload.name
        if payload.avatar_url:
            db_group.avatar_url = payload.avatar_url

        if payload.member_ids:
            db.query(GroupMember).filter(GroupMember.group_id == group_id).delete()
            for member_id in payload.member_ids:
                db.add(
                    GroupMember(
                        group_id=group_id,
                        user_id=member_id,
                        role="admin" if member_id == db_group.creator.id else "member",
                    )
                )

        db.commit()
        db.refresh(db_group)

        members = db.query(User).filter(User.id.in_(payload.member_ids)).all()

        return UpdateGroupSimpleResponse(
                id=db_group.id,
                group_name=db_group.name,
                members=[
                    GroupMemberSimpleResponse(
                        id=member.id,
                        full_name=member.full_name,
                        is_active=member.is_active,
                        is_online=getattr(member, "is_online", False),
                        avatar_url=member.avatar_url,
                    )
                    for member in members
                ],
            )
        