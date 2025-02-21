from sqlalchemy import Column, Integer, String, Text, ForeignKey, Boolean, TIMESTAMP, CheckConstraint, UniqueConstraint, func
from sqlalchemy.orm import relationship
from app.models.model_base import BareBaseModel

class Friend(BareBaseModel):
    __tablename__ = 'friends'
    
    user_id = Column(Integer, ForeignKey('users.id'), primary_key=True)
    friend_id = Column(Integer, ForeignKey('users.id'), primary_key=True)
    status = Column(String(20), CheckConstraint("status IN ('pending', 'accepted', 'blocked')"))
    friend_nick_name = Column(String(100))
    
    user = relationship("User", foreign_keys=[user_id])
    friend = relationship("User", foreign_keys=[friend_id])
