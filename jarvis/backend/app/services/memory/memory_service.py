from __future__ import annotations

import re
import uuid
from datetime import datetime, timezone
from typing import List, Optional
import aiosqlite
from loguru import logger
from app.models.memory_entry import MemoryEntry

class MemoryService:
    """Service for storing, searching, and extracting persistent conversational memories."""

    # Patterns for detecting user personal statements to auto-remember
    FACT_PATTERNS = [
        (re.compile(r"(?:my name is|i am called|call me)\s+([A-Za-z0-9_\- ]+)", re.I), "User Name"),
        (re.compile(r"(?:i live in|i am from|i'm located in)\s+([A-Za-z0-9_\-, ]+)", re.I), "User Location"),
        (re.compile(r"(?:i work as|i am an?)\s+([A-Za-z0-9_\- ]+)", re.I), "User Profession"),
        (re.compile(r"(?:my favorite|i prefer|i like)\s+([A-Za-z0-9_\- ]+)", re.I), "User Preference"),
        (re.compile(r"(?:remember that|note that|don't forget that)\s+([A-Za-z0-9_\- ,.'\"]+)", re.I), "User Note"),
    ]

    async def save_memory(
        self,
        conn: aiosqlite.Connection,
        conversation_id: Optional[str],
        key: str,
        value: str,
        relevance_score: float = 1.0,
    ) -> MemoryEntry:
        mem_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc)

        # Check if identical key exists
        cursor = await conn.execute(
            "SELECT id FROM memory_entries WHERE key = ? AND (conversation_id = ? OR conversation_id IS NULL);",
            (key, conversation_id),
        )
        existing = await cursor.fetchone()

        if existing:
            await conn.execute(
                """
                UPDATE memory_entries
                SET value = ?, relevance_score = ?, created_at = ?
                WHERE id = ?;
                """,
                (value, relevance_score, now.isoformat(), existing["id"]),
            )
            await conn.commit()
            return MemoryEntry(
                id=existing["id"],
                conversation_id=conversation_id,
                key=key,
                value=value,
                created_at=now,
                relevance_score=relevance_score,
            )

        await conn.execute(
            """
            INSERT INTO memory_entries (id, conversation_id, key, value, created_at, relevance_score)
            VALUES (?, ?, ?, ?, ?, ?);
            """,
            (mem_id, conversation_id, key, value, now.isoformat(), relevance_score),
        )
        await conn.commit()
        logger.info("Saved memory: [{}] = '{}'", key, value)
        return MemoryEntry(
            id=mem_id,
            conversation_id=conversation_id,
            key=key,
            value=value,
            created_at=now,
            relevance_score=relevance_score,
        )

    async def get_memories(
        self,
        conn: aiosqlite.Connection,
        conversation_id: Optional[str] = None,
        limit: int = 20,
    ) -> List[MemoryEntry]:
        if conversation_id:
            query = """
            SELECT id, conversation_id, key, value, created_at, relevance_score
            FROM memory_entries
            WHERE conversation_id = ? OR conversation_id IS NULL
            ORDER BY relevance_score DESC, created_at DESC
            LIMIT ?;
            """
            cursor = await conn.execute(query, (conversation_id, limit))
        else:
            query = """
            SELECT id, conversation_id, key, value, created_at, relevance_score
            FROM memory_entries
            ORDER BY relevance_score DESC, created_at DESC
            LIMIT ?;
            """
            cursor = await conn.execute(query, (limit,))

        rows = await cursor.fetchall()
        return [
            MemoryEntry(
                id=r["id"],
                conversation_id=r["conversation_id"],
                key=r["key"],
                value=r["value"],
                created_at=datetime.fromisoformat(r["created_at"]),
                relevance_score=r["relevance_score"],
            )
            for r in rows
        ]

    async def delete_memory(self, conn: aiosqlite.Connection, memory_id: str) -> bool:
        cursor = await conn.execute("DELETE FROM memory_entries WHERE id = ?;", (memory_id,))
        await conn.commit()
        return cursor.rowcount > 0

    async def extract_and_save_memories(
        self,
        conn: aiosqlite.Connection,
        conversation_id: Optional[str],
        text: str,
    ) -> List[MemoryEntry]:
        saved: List[MemoryEntry] = []
        for pattern, key_label in self.FACT_PATTERNS:
            match = pattern.search(text)
            if match:
                val = match.group(1).strip()
                if val and len(val) > 2:
                    entry = await self.save_memory(conn, conversation_id, key_label, val)
                    saved.append(entry)
        return saved

memory_service = MemoryService()
