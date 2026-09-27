from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
import aiosqlite
from pydantic import BaseModel

from app.database.connection import get_db
from app.models.memory_entry import MemoryEntry
from app.services.memory.memory_service import memory_service

router = APIRouter(prefix="/memory", tags=["Memory"])

class CreateMemoryRequest(BaseModel):
    conversation_id: Optional[str] = None
    key: str
    value: str
    relevance_score: float = 1.0

@router.get("/{conversation_id}", response_model=List[MemoryEntry])
async def get_memories(conversation_id: str, conn: aiosqlite.Connection = Depends(get_db)):
    return await memory_service.get_memories(conn, conversation_id)

@router.post("", response_model=MemoryEntry, status_code=status.HTTP_201_CREATED)
async def create_memory(req: CreateMemoryRequest, conn: aiosqlite.Connection = Depends(get_db)):
    return await memory_service.save_memory(conn, req.conversation_id, req.key, req.value, req.relevance_score)

@router.delete("/{memory_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_memory(memory_id: str, conn: aiosqlite.Connection = Depends(get_db)):
    success = await memory_service.delete_memory(conn, memory_id)
    if not success:
        raise HTTPException(status_code=404, detail="Memory entry not found")
