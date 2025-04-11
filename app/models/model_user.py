from sqlalchemy import Boolean, Column, String, Text
from sqlalchemy.orm import relationship

from app.models.model_base import BareBaseModel


class User(BareBaseModel):
    __tablename__ = "users"

    phone = Column(String(20), unique=True, nullable=False)
    full_name = Column(String(100), nullable=False)
    password_hash = Column(Text, nullable=False)
    avatar_url = Column(Text)
    status = Column(Text, default="Available")
    is_active = Column(Boolean, default=True)
    is_online = Column(Boolean, default=False)

    friends = relationship("Friend", foreign_keys="[Friend.user_id]")
    groups = relationship("Group", back_populates="creator")
    group_members = relationship("GroupMember", back_populates="user")

    sent_messages = relationship(
        "MessageModel", back_populates="sender", foreign_keys="[MessageModel.sender_id]"
    )
    sent_reactions = relationship(
        "MessageReactionModel",
        back_populates="sender",
        foreign_keys="[MessageReactionModel.user_id]",
    )
