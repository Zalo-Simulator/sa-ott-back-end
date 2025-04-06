from sqlalchemy import Column, Integer, String, Text, ForeignKey, Boolean, TIMESTAMP, CheckConstraint, UniqueConstraint, func
from sqlalchemy.orm import relationship
from app.models.model_base import BareBaseModel

class User(BareBaseModel):
    __tablename__ = 'users'
    
    phone = Column(String(20), unique=True, nullable=False)
    full_name = Column(String(100), nullable=False)
    password_hash  = Column(Text, nullable=False)
    avatar_url = Column(Text)
    status = Column(Text, default='Available')
    is_active = Column(Boolean, default=True)

    friends = relationship("Friend", foreign_keys="[Friend.user_id]")
    groups = relationship("Group", back_populates="creator")


