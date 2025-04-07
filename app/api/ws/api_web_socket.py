import json
from datetime import datetime
from typing import Dict, List, Optional
import logging
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

# Store active WebSocket connections mapped by user ID
clients: Dict[str, WebSocket] = {}

# Fake user status and message DB (replace with real DB in production)
user_status: Dict[str, bool] = {}
chat_messages: List[Dict] = []

router = APIRouter()

logger = logging.getLogger()


@router.websocket("/users/{user_id}")
async def websocket_endpoint(
    *,
    websocket: WebSocket,
    user_id: str,
    q: Optional[int] = None,
    cookie_or_token: Optional[str] = None,
):
    await websocket.accept()
    clients[user_id] = websocket
    user_status[user_id] = True
    logger.info(f"✅ User {user_id} connected! Online status updated.")

    try:
        while True:
            data = await websocket.receive_text()
            logger.info(f"📩 Received from {user_id}: {data}")

            try:
                json_data = json.loads(data)
            except Exception as e:
                logger.error(f"❌ Error parsing JSON: {e}")
                await websocket.send_text("⚠️ Invalid JSON format.")
                return

            if "message" not in json_data or "group_id" not in json_data:
                await websocket.send_text(
                    '⚠️ Invalid data. Use \'{{"group_id": "<id>", "message": "<message>"}}\''
                )
            else:
                group_id, message = json_data["group_id"], json_data["message"]
                timestamp = datetime.now().isoformat()

                # Save message
                chat_messages.append({
                    "from": user_id,
                    "to": group_id,
                    "message": message,
                    "timestamp": timestamp,
                })
                logger.info(f"💾 Message saved: {user_id} ➜ {group_id}: {message}")

                # Forward message if target is connected
                if group_id in clients:
                    await clients[group_id].send_text(f"{user_id}: {message}")
                    logger.info(f"📤 Sent to {group_id}: {message}")
                else:
                    logger.warning(
                        f"⚠️ User {group_id} is offline. Message not delivered."
                    )

    except WebSocketDisconnect:
        logger.error(f"❌ User {user_id} disconnected!")
        user_status[user_id] = False
        clients.pop(user_id, None)
