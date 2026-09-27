from typing import Optional
from pydantic import BaseModel

class SettingsResponse(BaseModel):
    model: str
    whisper_model: str
    piper_voice: str
    voice_output_enabled: bool
    memory_enabled: bool

class UpdateSettingsRequest(BaseModel):
    model: Optional[str] = None
    whisper_model: Optional[str] = None
    piper_voice: Optional[str] = None
    voice_output_enabled: Optional[bool] = None
    memory_enabled: Optional[bool] = None
