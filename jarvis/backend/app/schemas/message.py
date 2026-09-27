from datetime import datetime
from typing import Literal, Optional
from pydantic import BaseModel

class MessageResponse(BaseModel):
    id: str
    conversation_id: str
    role: Literal["user", "assistant", "system"]
    content: str
    timestamp: datetime
    tokens_used: Optional[int] = None
    audio_path: Optional[str] = None

class SendMessageRequest(BaseModel):
    conversation_id: str
    content: str
    use_voice: bool = False
