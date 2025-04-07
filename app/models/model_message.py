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


class MessageModel(BareBaseModel):
    __tablename__ = "messages"

    message_id = Column(Integer, primary_key=True)
    group_id = Column(Integer, ForeignKey("conversations.group_id"))
    sender_id = Column(Integer, ForeignKey("users.user_id"))
    content = Column(Text)  # Chứa nội dung tin nhắn (có thể null)
    message_type = Column(
        String(10),
        CheckConstraint(
            "message_type IN ('text', 'image', 'video', 'file', 'sticker')"
        ),
    )
    attachment_id = Column(Text)  # URL chứa file (ảnh, video, file, hoặc sticker)
    created_at = Column(TIMESTAMP, default=func.now())


class MessageReactionModel(BareBaseModel):
    __tablename__ = "message_reactions"

    message_id = Column(Integer, ForeignKey("messages.message_id"), primary_key=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), primary_key=True)
    reaction = Column(
        String(10)
    )  # Ví dụ: 😀, ❤️, 👍 # mã code icon, còn render icon này như thế nào là do FE tự mapping vs icon_url
    count = Column(Integer, default=1)  # số lượng reaction mà người đó gửi


class AttachmentModel(BareBaseModel):
    __tablename__ = "attachments"

    attachment_id = Column(Integer, primary_key=True)
    file_url = Column(Text, nullable=False)
    file_type = Column(
        String(10),
        CheckConstraint("file_type IN ('image', 'video', 'file', 'sticker')"),
    )
    file_size = Column(Integer)  # Optional
