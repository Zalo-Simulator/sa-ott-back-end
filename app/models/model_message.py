from sqlalchemy import (
    TIMESTAMP,
    CheckConstraint,
    Column,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
)

from app.models.model_base import BareBaseModel
from sqlalchemy.orm import relationship


class MessageModel(BareBaseModel):
    __tablename__ = "messages"

    group_id = Column(Integer, ForeignKey("groups.id"))
    sender_id = Column(Integer, ForeignKey("users.id"))
    content = Column(Text)  # Chứa nội dung tin nhắn (có thể null)
    message_type = Column(
        String(10),
        CheckConstraint(
            "message_type IN ('text', 'image', 'video', 'file', 'sticker')"
        ),
    )
    attachment_id = Column(Integer)  # URL chứa file (ảnh, video, file, hoặc sticker)

    sender = relationship("User", back_populates="sent_messages")
    reactions = relationship("MessageReactionModel", back_populates="message")


class MessageReactionModel(BareBaseModel):
    __tablename__ = "message_reactions"

    message_id = Column(Integer, ForeignKey("messages.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    reaction = Column(
        String(10)
    )  # Ví dụ: 😀, ❤️, 👍 # mã code icon, còn render icon này như thế nào là do FE tự mapping vs icon_url
    count = Column(Integer, default=1)  # số lượng reaction mà người đó gửi

    sender = relationship("User", back_populates="sent_reactions")
    message = relationship("MessageModel", back_populates="reactions")


class AttachmentModel(BareBaseModel):
    __tablename__ = "attachments"

    file_url = Column(Text, nullable=False)
    file_type = Column(
        String(10),
        CheckConstraint("file_type IN ('image', 'video', 'file', 'sticker')"),
    )
    file_size = Column(Integer)  # Optional
