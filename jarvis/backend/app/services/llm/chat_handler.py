from __future__ import annotations

from typing import AsyncIterator, Optional, List
import aiosqlite
from datetime import datetime, timezone
import uuid
from loguru import logger

from app.models.message import Message
from app.models.memory_entry import MemoryEntry
from app.services.llm.ollama_client import ollama_client
from app.services.llm.prompt_builder import PromptBuilder
from app.config import get_settings

class ChatHandler:
    """Orchestrates message history retrieval, memory augmentation, LLM streaming, and message persistence."""

    def __init__(self):
        self.settings = get_settings()

    async def get_conversation_history(self, conn: aiosqlite.Connection, conversation_id: str, limit: int = 20) -> List[Message]:
        cursor = await conn.execute(
            """
            SELECT id, conversation_id, role, content, timestamp, tokens_used, audio_path
            FROM messages
            WHERE conversation_id = ?
            ORDER BY timestamp ASC
            LIMIT ?;
            """,
            (conversation_id, limit),
        )
        rows = await cursor.fetchall()
        messages: List[Message] = []
        for row in rows:
            messages.append(
                Message(
                    id=row["id"],
                    conversation_id=row["conversation_id"],
                    role=row["role"],
                    content=row["content"],
                    timestamp=datetime.fromisoformat(row["timestamp"]),
                    tokens_used=row["tokens_used"],
                    audio_path=row["audio_path"],
                )
            )
        return messages

    async def get_memories(self, conn: aiosqlite.Connection, conversation_id: str, limit: int = 10) -> List[MemoryEntry]:
        cursor = await conn.execute(
            """
            SELECT id, conversation_id, key, value, created_at, relevance_score
            FROM memory_entries
            WHERE conversation_id = ? OR conversation_id IS NULL
            ORDER BY relevance_score DESC, created_at DESC
            LIMIT ?;
            """,
            (conversation_id, limit),
        )
        rows = await cursor.fetchall()
        memories: List[MemoryEntry] = []
        for row in rows:
            memories.append(
                MemoryEntry(
                    id=row["id"],
                    conversation_id=row["conversation_id"],
                    key=row["key"],
                    value=row["value"],
                    created_at=datetime.fromisoformat(row["created_at"]),
                    relevance_score=row["relevance_score"],
                )
            )
        return memories

    async def persist_message(
        self,
        conn: aiosqlite.Connection,
        conversation_id: str,
        role: str,
        content: str,
        tokens_used: Optional[int] = None,
        audio_path: Optional[str] = None,
    ) -> Message:
        msg_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc)
        await conn.execute(
            """
            INSERT INTO messages (id, conversation_id, role, content, timestamp, tokens_used, audio_path)
            VALUES (?, ?, ?, ?, ?, ?, ?);
            """,
            (msg_id, conversation_id, role, content, now.isoformat(), tokens_used, audio_path),
        )
        await conn.execute(
            "UPDATE conversations SET updated_at = ? WHERE id = ?;",
            (now.isoformat(), conversation_id),
        )
        await conn.commit()
        return Message(
            id=msg_id,
            conversation_id=conversation_id,
            role=role,  # type: ignore
            content=content,
            timestamp=now,
            tokens_used=tokens_used,
            audio_path=audio_path,
        )

    async def ensure_conversation(self, conn: aiosqlite.Connection, conversation_id: str, model_used: Optional[str] = None):
        cursor = await conn.execute("SELECT id FROM conversations WHERE id = ?;", (conversation_id,))
        row = await cursor.fetchone()
        now = datetime.now(timezone.utc).isoformat()
        if not row:
            await conn.execute(
                """
                INSERT INTO conversations (id, title, created_at, updated_at, model_used, is_archived)
                VALUES (?, ?, ?, ?, ?, 0);
                """,
                (conversation_id, "New Conversation", now, now, model_used or self.settings.OLLAMA_MODEL),
            )
            await conn.commit()

    async def stream_response(
        self,
        conn: aiosqlite.Connection,
        conversation_id: str,
        user_message: str,
        model: Optional[str] = None,
    ) -> AsyncIterator[str]:
        await self.ensure_conversation(conn, conversation_id, model)
        await self.persist_message(conn, conversation_id, "user", user_message)

        history = await self.get_conversation_history(conn, conversation_id, limit=self.settings.MAX_CONVERSATION_HISTORY)
        memories = await self.get_memories(conn, conversation_id, limit=self.settings.MEMORY_CONTEXT_WINDOW)

        system_prompt = PromptBuilder.build_system_prompt(memories)
        # Exclude the last message from history since build_messages appends user_message
        prior_history = [m for m in history if m.content != user_message or m.role != "user"]
        messages = PromptBuilder.build_messages(prior_history, user_message, system_prompt)

        tokens_acc: List[str] = []
        try:
            async for token in ollama_client.stream_chat(messages, model=model):
                tokens_acc.append(token)
                yield token
        finally:
            full_response = "".join(tokens_acc).strip()
            if full_response:
                await self.persist_message(conn, conversation_id, "assistant", full_response)

chat_handler = ChatHandler()
