from __future__ import annotations

from typing import List, Optional, Dict
import aiosqlite
from datetime import datetime
from app.models.message import Message
from app.models.memory_entry import MemoryEntry
from app.services.memory.memory_service import memory_service

class ContextRetriever:
    """Retrieves conversation messages and prioritizes relevant memory tokens for LLM context."""

    async def get_conversation_context(
        self,
        conn: aiosqlite.Connection,
        conversation_id: str,
        limit: int = 20,
    ) -> List[Message]:
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
        return [
            Message(
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

    async def get_relevant_memories(
        self,
        conn: aiosqlite.Connection,
        conversation_id: str,
        query: Optional[str] = None,
        limit: int = 10,
    ) -> List[MemoryEntry]:
        all_memories = await memory_service.get_memories(conn, conversation_id, limit=50)
        if not query:
            return all_memories[:limit]

        # Simple keyword ranking
        query_words = set(query.lower().split())
        scored_memories = []
        for mem in all_memories:
            mem_words = set((mem.key + " " + mem.value).lower().split())
            intersection = query_words.intersection(mem_words)
            score = mem.relevance_score + (len(intersection) * 2.0)
            scored_memories.append((score, mem))

        scored_memories.sort(key=lambda x: x[0], reverse=True)
        return [mem for _, mem in scored_memories[:limit]]

    def format_context_for_llm(self, messages: List[Message]) -> List[Dict[str, str]]:
        return [{"role": m.role, "content": m.content} for m in messages]

context_retriever = ContextRetriever()
