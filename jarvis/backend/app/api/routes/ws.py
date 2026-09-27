import json
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from loguru import logger
import aiosqlite

from app.database.connection import db_manager
from app.websocket.connection_manager import manager
from app.websocket.message_handler import message_handler
from app.websocket.events import EventType

router = APIRouter(tags=["WebSocket"])

@router.websocket("/ws/{conversation_id}")
async def websocket_endpoint(websocket: WebSocket, conversation_id: str):
    await manager.connect(conversation_id, websocket)
    conn = await db_manager.get_connection()
    try:
        while True:
            msg = await websocket.receive()
            if "bytes" in msg and msg["bytes"]:
                # Binary audio chunk received
                await message_handler.handle_audio_chunk(conversation_id, msg["bytes"])
            elif "text" in msg and msg["text"]:
                try:
                    payload = json.loads(msg["text"])
                    event = payload.get("event") or payload.get("type")
                    data = payload.get("data") or payload.get("content")

                    if event in (EventType.AUDIO_CHUNK, "audio_chunk"):
                        pass
                    elif event in (EventType.AUDIO_END, "audio_end"):
                        await message_handler.handle_audio_end(conversation_id, manager, conn)
                    elif event in (EventType.TEXT_MESSAGE, "text_message", "text"):
                        text_content = data if isinstance(data, str) else str(data)
                        await message_handler.handle_text_message(conversation_id, text_content, manager, conn)
                    elif event in (EventType.CANCEL_GENERATION, "cancel_generation", "cancel"):
                        await message_handler.handle_cancel_generation(conversation_id, manager)
                    elif event in (EventType.PING, "ping"):
                        await manager.send_json(conversation_id, {"event": EventType.PONG, "data": "pong"})
                except json.JSONDecodeError:
                    logger.warning("Invalid JSON received over WebSocket in conv: {}", conversation_id)
    except WebSocketDisconnect:
        await manager.disconnect(conversation_id, websocket)
    except Exception as e:
        logger.error("Unexpected WebSocket error in {}: {}", conversation_id, e)
        await manager.disconnect(conversation_id, websocket)
    finally:
        await conn.close()
