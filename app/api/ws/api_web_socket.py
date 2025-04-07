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
from app.models.model_message import MessageModel
from app.db.base import get_db
from app.models.model_group import GroupMember

# Store active WebSocket connections mapped by user ID
clients: Dict[int, WebSocket] = {}

# # Fake user status and message DB (replace with real DB in production)
# user_status: Dict[str, bool] = {}
chat_messages: List[Dict] = []

router = APIRouter()

logger = logging.getLogger()


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

            if "message" not in json_data or "group_id" not in json_data:
                await websocket.send_text(
                    '⚠️ Invalid data. Use \'{{"group_id": <id:int>, "message": "<message>"}}\''
                )

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

            message: str = json_data["message"]
            timestamp = datetime.now().isoformat()

            # Save message
            db_message = MessageModel(
                group_id=group_id,
                sender_id=user_id,
                content=message,
                created_at=timestamp,
                message_type="text",
            )
            db.add(db_message)
            db.commit()
            db.refresh(db_message)

            logger.info(f"💾 Message saved: {user_id} ➜ {group_id}: {message}")

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
                    await clients[target_id].send_text(f"{user_id}: {message}")
                    logger.info(f"📤 Sent to {group_id}: {message}")
            else:
                logger.warning(f"⚠️ User {group_id} is offline. Message not delivered.")

    except WebSocketDisconnect:
        logger.error(f"❌ User {user_id} disconnected!")
        # user_status[user_id] = False
        clients.pop(user_id, None)
