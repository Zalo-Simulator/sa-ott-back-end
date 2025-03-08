from sqlalchemy import Column, Integer, String, Text, ForeignKey, Boolean, TIMESTAMP, CheckConstraint, UniqueConstraint, func
from sqlalchemy.orm import relationship
from app.models.model_base import BareBaseModel


class Group(BareBaseModel):
    __tablename__ = 'groups'
    
    name = Column(String(255), nullable=False)
    avatar_url = Column(Text)
    created_by = Column(Integer, ForeignKey('users.id'))
    type = Column(String(10), CheckConstraint("type IN ('private', 'group')"))
    visible = Column(Boolean, nullable=False)
    
    creator = relationship("User", back_populates="groups")
    
class GroupMember(BareBaseModel):
    __tablename__ = 'group_members'

    group_id = Column(Integer, ForeignKey('groups.id'), primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), primary_key=True)
    role = Column(String(20), CheckConstraint("role IN ('admin', 'member')"))
    
