import json
import logging
from datetime import datetime
from typing import Dict, List, Optional

from fastapi import (
    APIRouter,
    Depends,
    WebSocket,
    WebSocketDisconnect,
)
from sqlalchemy.orm import Session
from app.models.model_message import MessageModel, MessageReactionModel
from app.db.base import get_db
from app.models.model_group import GroupMember
from typing import TypedDict

# Store active WebSocket connections mapped by user ID
clients: Dict[int, WebSocket] = {}

# # Fake user status and message DB (replace with real DB in production)
# user_status: Dict[str, bool] = {}
chat_messages: List[Dict] = []

router = APIRouter()

logger = logging.getLogger()


class DataDict(TypedDict):
    message_type: str  # text, image, video, file, sticker, reaction
    group_id: int  # ID of the group to send message to
    message: Optional[str]
    message_id: Optional[int]  # ID of the message to react to
    reaction: Optional[str]  # reaction type


@router.websocket("/users/{user_id}")
async def websocket_endpoint(
    *,
    websocket: WebSocket,
    user_id: int,
    db: Session = Depends(get_db),
    q: Optional[int] = None,
    cookie_or_token: Optional[str] = None,
):
    await websocket.accept()
    clients[user_id] = websocket
    # user_status[user_id] = True
    logger.info(f"✅ User {user_id} connected! Online status updated.")

    try:
        while True:
            json_dump_data = await websocket.receive_text()
            logger.info(f"📩 Received from {user_id}: {json_dump_data}")

            try:
                json_data = json.loads(json_dump_data)
            except Exception as e:
                logger.error(f"❌ Error parsing JSON: {e}")
                await websocket.send_text("⚠️ Invalid JSON format.")
                raise

            if "message_type" not in json_data or "group_id" not in json_data:
                await websocket.send_text(
                    '⚠️ Invalid data. Use \'{{"message_type": "<message_type>", "group_id": "<group_id:int>" }}\''
                )

            # Group validation: Is that group valid and user is a member of that group?
            group_id: int = json_data["group_id"]
            if isinstance(group_id, str):
                try:
                    group_id = int(group_id)
                except ValueError:
                    logger.error(f"❌ Invalid group_id: {group_id}")
                    await websocket.send_text("⚠️ Invalid group ID.")
                    raise

            db_group_member = (
                db.query(GroupMember)
                .filter(
                    GroupMember.group_id == group_id, GroupMember.user_id == user_id
                )
                .first()
            )
            if db_group_member is None:
                logger.error(
                    f"❌ GroupMember not found for group_id={group_id} and user_id={user_id}."
                )
                await websocket.send_text("⚠️ Group or user not found.")
                raise

            # Reaction validation: Is that reaction valid?
            if (
                json_data["message_type"] == "reaction"
                and "message_id" in json_data
                and "reaction" in json_data
            ):
                message_id: int = json_data["message_id"]
                if isinstance(message_id, str):
                    try:
                        message_id = int(message_id)
                    except ValueError:
                        logger.error(f"❌ Invalid message_id: {message_id}")
                        await websocket.send_text("⚠️ Invalid message ID.")
                        raise
                reaction: str = json_data["reaction"]
                db_message_reaction: MessageReactionModel = (
                    db.query(MessageReactionModel)
                    .filter(
                        (MessageReactionModel.message_id == message_id)
                        & (MessageReactionModel.user_id == user_id)
                        & (MessageReactionModel.reaction == reaction)
                    )
                    .first()
                )
                if db_message_reaction is None:
                    db_message_reaction = MessageReactionModel(
                        message_id=message_id,
                        user_id=user_id,
                        reaction=reaction,
                        count=1,
                    )
                    db.add(db_message_reaction)
                else:
                    db_message_reaction.count += 1
                db.commit()
                db.refresh(db_message_reaction)
                logger.info(f"💾 Reaction saved: {user_id} ➜ {message_id}: {reaction}")

                response_data_string = json_dump_data

            # Message validation: Is that message valid?
            elif (
                json_data["message_type"]
                in ["image", "video", "file", "sticker", "text"]
                and "message" in json_data
            ):
                message: str = json_data["message"]
                timestamp = datetime.now().isoformat()

                # Save message
                db_message = MessageModel(
                    group_id=group_id,
                    sender_id=user_id,
                    content=message,
                    created_at=timestamp,
                    message_type=json_data["message_type"],
                )
                db.add(db_message)
                db.commit()
                db.refresh(db_message)

                logger.info(f"💾 Message saved: {user_id} ➜ {group_id}: {message}")

                json_data["message_id"] = db_message.id
                json_data["created_at"] = db_message.created_at.isoformat()
                response_data_string = json.dumps(json_data)

            # Media validation: Is that media valid?
            # if (
            #     json_data["message_type"] in ["image", "video", "file", "sticker"]
            #     and "message" in json_data
            # ):
            #     pass

            else:
                response_data_string = json.dumps(json_data)

            # Forward message if target is connected
            db_group_member_target = (
                db.query(GroupMember)
                .filter(
                    (GroupMember.group_id == group_id)
                    & (GroupMember.user_id != user_id)
                )
                .all()
            )

            for member in db_group_member_target:
                target_id = member.user_id
                if target_id not in clients:
                    logger.info(
                        f"⚠️ User {target_id} is offline. Message not delivered."
                    )
                    continue

                if target_id in clients:
                    await clients[target_id].send_text(response_data_string)
                    logger.info(f"📤 Sent to {group_id}: {response_data_string}")
                else:
                    logger.info(f"⚠️ User {group_id} is offline. Message not delivered.")

    except WebSocketDisconnect:
        logger.error(f"❌ User {user_id} disconnected!")
        # user_status[user_id] = False
        clients.pop(user_id, None)
