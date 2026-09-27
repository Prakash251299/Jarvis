from datetime import datetime, timezone
from typing import Literal, Optional
from pydantic import BaseModel, Field
import uuid

class Message(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    conversation_id: str
    role: Literal["user", "assistant", "system"]
    content: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    tokens_used: Optional[int] = None
    audio_path: Optional[str] = None

class MessageCreate(BaseModel):
    conversation_id: str
    role: Literal["user", "assistant", "system"]
    content: str
    tokens_used: Optional[int] = None
    audio_path: Optional[str] = None
