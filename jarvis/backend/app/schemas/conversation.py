from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict

class CreateConversationRequest(BaseModel):
    title: Optional[str] = "New Conversation"
    model: Optional[str] = None

class ConversationResponse(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    id: str
    title: str
    created_at: datetime
    updated_at: datetime
    model_used: str
    is_archived: bool
    message_count: int = 0

class ConversationListResponse(BaseModel):
    conversations: List[ConversationResponse]
    total: int
