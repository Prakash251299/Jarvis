from fastapi import APIRouter, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel
from typing import Optional, List
from app.services.tts.piper_service import piper_service

router = APIRouter(prefix="/tts", tags=["TTS"])

class SynthesizeRequest(BaseModel):
    text: str
    voice: Optional[str] = None

@router.post("/synthesize")
async def synthesize_speech(req: SynthesizeRequest):
    if not req.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty")

    audio_bytes = await piper_service.synthesize(req.text, voice=req.voice)
    if not audio_bytes:
        raise HTTPException(status_code=500, detail="Speech synthesis failed")

    return Response(content=audio_bytes, media_type="audio/wav")

@router.get("/voices", response_model=List[str])
async def list_voices():
    return piper_service.list_voices()
