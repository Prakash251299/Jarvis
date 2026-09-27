from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from pydantic import BaseModel
from typing import Optional
from app.services.stt.whisper_service import whisper_service
from app.services.stt.audio_utils import validate_audio

router = APIRouter(prefix="/stt", tags=["STT"])

class TranscriptionResponse(BaseModel):
    text: str
    language: str
    duration: float

@router.post("/transcribe", response_model=TranscriptionResponse)
async def transcribe_audio(
    file: UploadFile = File(...),
    language: Optional[str] = Form(default="en"),
):
    audio_bytes = await file.read()
    if not audio_bytes:
        raise HTTPException(status_code=400, detail="Empty audio file provided")

    if not validate_audio(audio_bytes):
        raise HTTPException(status_code=415, detail="Unsupported or invalid audio format")

    result = await whisper_service.transcribe(audio_bytes, language=language)
    return TranscriptionResponse(
        text=result.text,
        language=result.language,
        duration=result.duration,
    )

@router.get("/health")
async def stt_health():
    healthy = await whisper_service.health_check()
    return {"status": "ok" if healthy else "unavailable"}
