from __future__ import annotations

from enum import Enum
from typing import Any, Optional
from pydantic import BaseModel

class EventType(str, Enum):
    # Client -> Server
    AUDIO_CHUNK = "audio_chunk"
    AUDIO_END = "audio_end"
    TEXT_MESSAGE = "text_message"
    CANCEL_GENERATION = "cancel_generation"
    PING = "ping"

    # Server -> Client
    TRANSCRIPTION = "transcription"
    TOKEN = "token"
    GENERATION_START = "generation_start"
    GENERATION_END = "generation_end"
    AUDIO_RESPONSE = "audio_response"
    ERROR = "error"
    PONG = "pong"
    STATUS = "status"

class WebSocketMessage(BaseModel):
    event: EventType
    data: Optional[Any] = None
    conversation_id: Optional[str] = None
    message_id: Optional[str] = None
