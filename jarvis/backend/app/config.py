from functools import lru_cache
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    APP_NAME: str = "Jarvis AI Assistant"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    DATABASE_URL: str = "sqlite+aiosqlite:///./jarvis.db"
    DB_PATH: str = "./jarvis.db"

    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "qwen3:8b"
    OLLAMA_TIMEOUT: float = 120.0

    WHISPER_MODEL: str = "base"
    WHISPER_DEVICE: str = "cpu"
    WHISPER_COMPUTE_TYPE: str = "int8"

    PIPER_VOICE: str = "en_US-lessac-medium"
    PIPER_DATA_DIR: str = str(Path.home() / ".local/share/piper")
    PIPER_SAMPLE_RATE: int = 22050

    MEMORY_CONTEXT_WINDOW: int = 10
    MAX_CONVERSATION_HISTORY: int = 20
    CORS_ORIGINS: List[str] = ["*"]

@lru_cache()
def get_settings() -> Settings:
    return Settings()
