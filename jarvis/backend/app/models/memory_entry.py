from datetime import datetime, timezone
from typing import Optional
from pydantic import BaseModel, Field
import uuid

class MemoryEntry(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    conversation_id: Optional[str] = None
    key: str
    value: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    relevance_score: float = 1.0

class MemoryEntryCreate(BaseModel):
    conversation_id: Optional[str] = None
    key: str
    value: str
    relevance_score: float = 1.0
