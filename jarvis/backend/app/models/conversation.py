from datetime import datetime, timezone
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict
import uuid

class Conversation(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str = "New Conversation"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    model_used: str = "qwen3:8b"
    is_archived: bool = False

class ConversationCreate(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    title: Optional[str] = "New Conversation"
    model_used: Optional[str] = "qwen3:8b"

class ConversationUpdate(BaseModel):
    title: Optional[str] = None
    is_archived: Optional[bool] = None
