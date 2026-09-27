from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
import aiosqlite

from app.database.connection import get_db
from app.services.llm.ollama_client import ollama_client
from app.services.llm.chat_handler import chat_handler

router = APIRouter(prefix="/llm", tags=["LLM"])

class ChatRequest(BaseModel):
    conversation_id: str
    message: str
    model: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    conversation_id: str

@router.get("/models", response_model=List[str])
async def list_models():
    models = await ollama_client.list_models()
    return models

@router.get("/health")
async def check_health():
    is_healthy = await ollama_client.check_health()
    if not is_healthy:
        raise HTTPException(status_code=503, detail="Ollama server not reachable")
    return {"status": "ok", "service": "ollama"}

@router.post("/chat", response_model=ChatResponse)
async def non_streaming_chat(req: ChatRequest, conn: aiosqlite.Connection = Depends(get_db)):
    tokens = []
    async for token in chat_handler.stream_response(conn, req.conversation_id, req.message, model=req.model):
        tokens.append(token)
    return ChatResponse(response="".join(tokens), conversation_id=req.conversation_id)
