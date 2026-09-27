from typing import List
import uuid
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
import aiosqlite

from app.database.connection import get_db
from app.schemas.conversation import ConversationResponse, ConversationListResponse, CreateConversationRequest
from app.schemas.message import MessageResponse
from app.config import get_settings

router = APIRouter(prefix="/conversations", tags=["Conversations"])

@router.post("", response_model=ConversationResponse, status_code=status.HTTP_201_CREATED)
async def create_conversation(req: CreateConversationRequest, conn: aiosqlite.Connection = Depends(get_db)):
    settings = get_settings()
    conv_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()
    model = req.model or settings.OLLAMA_MODEL
    title = req.title or "New Conversation"

    await conn.execute(
        """
        INSERT INTO conversations (id, title, created_at, updated_at, model_used, is_archived)
        VALUES (?, ?, ?, ?, ?, 0);
        """,
        (conv_id, title, now, now, model),
    )
    await conn.commit()

    return ConversationResponse(
        id=conv_id,
        title=title,
        created_at=datetime.fromisoformat(now),
        updated_at=datetime.fromisoformat(now),
        model_used=model,
        is_archived=False,
        message_count=0,
    )

@router.get("", response_model=ConversationListResponse)
async def list_conversations(conn: aiosqlite.Connection = Depends(get_db)):
    cursor = await conn.execute(
        """
        SELECT c.id, c.title, c.created_at, c.updated_at, c.model_used, c.is_archived, COUNT(m.id) as message_count
        FROM conversations c
        LEFT JOIN messages m ON c.id = m.conversation_id
        WHERE c.is_archived = 0
        GROUP BY c.id
        ORDER BY c.updated_at DESC;
        """
    )
    rows = await cursor.fetchall()
    conversations = [
        ConversationResponse(
            id=r["id"],
            title=r["title"],
            created_at=datetime.fromisoformat(r["created_at"]),
            updated_at=datetime.fromisoformat(r["updated_at"]),
            model_used=r["model_used"],
            is_archived=bool(r["is_archived"]),
            message_count=r["message_count"],
        )
        for r in rows
    ]
    return ConversationListResponse(conversations=conversations, total=len(conversations))

@router.get("/{conversation_id}", response_model=ConversationResponse)
async def get_conversation(conversation_id: str, conn: aiosqlite.Connection = Depends(get_db)):
    cursor = await conn.execute(
        """
        SELECT c.id, c.title, c.created_at, c.updated_at, c.model_used, c.is_archived, COUNT(m.id) as message_count
        FROM conversations c
        LEFT JOIN messages m ON c.id = m.conversation_id
        WHERE c.id = ?
        GROUP BY c.id;
        """,
        (conversation_id,),
    )
    r = await cursor.fetchone()
    if not r:
        raise HTTPException(status_code=404, detail="Conversation not found")

    return ConversationResponse(
        id=r["id"],
        title=r["title"],
        created_at=datetime.fromisoformat(r["created_at"]),
        updated_at=datetime.fromisoformat(r["updated_at"]),
        model_used=r["model_used"],
        is_archived=bool(r["is_archived"]),
        message_count=r["message_count"],
    )

@router.delete("/{conversation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_conversation(conversation_id: str, conn: aiosqlite.Connection = Depends(get_db)):
    cursor = await conn.execute("DELETE FROM conversations WHERE id = ?;", (conversation_id,))
    await conn.commit()
    if cursor.rowcount == 0:
        raise HTTPException(status_code=404, detail="Conversation not found")

@router.get("/{conversation_id}/messages", response_model=List[MessageResponse])
async def get_messages(conversation_id: str, conn: aiosqlite.Connection = Depends(get_db)):
    cursor = await conn.execute(
        """
        SELECT id, conversation_id, role, content, timestamp, tokens_used, audio_path
        FROM messages
        WHERE conversation_id = ?
        ORDER BY timestamp ASC;
        """,
        (conversation_id,),
    )
    rows = await cursor.fetchall()
    return [
        MessageResponse(
            id=r["id"],
            conversation_id=r["conversation_id"],
            role=r["role"],
            content=r["content"],
            timestamp=datetime.fromisoformat(r["timestamp"]),
            tokens_used=r["tokens_used"],
            audio_path=r["audio_path"],
        )
        for r in rows
    ]
