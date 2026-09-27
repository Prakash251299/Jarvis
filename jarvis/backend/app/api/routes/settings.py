from datetime import datetime, timezone
from fastapi import APIRouter, Depends
import aiosqlite

from app.database.connection import get_db
from app.schemas.settings import SettingsResponse, UpdateSettingsRequest
from app.services.llm.ollama_client import ollama_client

router = APIRouter(prefix="/settings", tags=["Settings"])

@router.get("", response_model=SettingsResponse)
async def get_app_settings(conn: aiosqlite.Connection = Depends(get_db)):
    cursor = await conn.execute("SELECT key, value FROM settings;")
    rows = await cursor.fetchall()
    config_map = {r["key"]: r["value"] for r in rows}

    return SettingsResponse(
        model=config_map.get("model", "qwen3:8b"),
        whisper_model=config_map.get("whisper_model", "base"),
        piper_voice=config_map.get("piper_voice", "en_US-lessac-medium"),
        voice_output_enabled=config_map.get("voice_output_enabled", "true").lower() == "true",
        memory_enabled=config_map.get("memory_enabled", "true").lower() == "true",
    )

@router.put("", response_model=SettingsResponse)
@router.patch("", response_model=SettingsResponse)
async def update_app_settings(req: UpdateSettingsRequest, conn: aiosqlite.Connection = Depends(get_db)):
    now = datetime.now(timezone.utc).isoformat()
    fields = [
        ("model", req.model),
        ("whisper_model", req.whisper_model),
        ("piper_voice", req.piper_voice),
        ("voice_output_enabled", str(req.voice_output_enabled).lower() if req.voice_output_enabled is not None else None),
        ("memory_enabled", str(req.memory_enabled).lower() if req.memory_enabled is not None else None),
    ]
    for key, val in fields:
        if val is not None:
            await conn.execute(
                "INSERT INTO settings (key, value, updated_at) VALUES (?, ?, ?) ON CONFLICT(key) DO UPDATE SET value = excluded.value, updated_at = excluded.updated_at;",
                (key, val, now),
            )
    await conn.commit()
    return await get_app_settings(conn)

@router.get("/available-models")
async def get_available_models():
    return await ollama_client.list_models()
