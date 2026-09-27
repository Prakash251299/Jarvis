from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from loguru import logger
import sys

from app.config import get_settings
from app.database.connection import db_manager
from app.tools.tool_registry import registry
from app.api.routes import conversations, llm, stt, tts, memory, settings, ws

logger.remove()
logger.add(sys.stdout, colorize=True, format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>")

app_settings = get_settings()

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up Jarvis AI Assistant backend...")
    await db_manager.initialize()
    registry.auto_discover()
    logger.info("Loaded {} tools: {}", len(registry.list_tools()), [t.name for t in registry.list_tools()])
    yield
    logger.info("Shutting down Jarvis AI Assistant backend...")

app = FastAPI(
    title=app_settings.APP_NAME,
    version=app_settings.APP_VERSION,
    description="Production-quality local AI voice assistant backend with Ollama, Faster-Whisper, and Piper TTS.",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=app_settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API v1 routers
API_V1_PREFIX = "/api/v1"
app.include_router(conversations.router, prefix=API_V1_PREFIX)
app.include_router(llm.router, prefix=API_V1_PREFIX)
app.include_router(stt.router, prefix=API_V1_PREFIX)
app.include_router(tts.router, prefix=API_V1_PREFIX)
app.include_router(memory.router, prefix=API_V1_PREFIX)
app.include_router(settings.router, prefix=API_V1_PREFIX)

# WebSocket routes (both at root /ws and /api/v1/ws for client compatibility)
app.include_router(ws.router)
app.include_router(ws.router, prefix=API_V1_PREFIX)

@app.get("/health", tags=["Health"])
async def health_check():
    return {
        "status": "healthy",
        "app": app_settings.APP_NAME,
        "version": app_settings.APP_VERSION,
        "mode": "fully_local",
    }

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error("Unhandled exception for {}: {}", request.url, exc)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error occurred.", "error": str(exc)},
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host=app_settings.HOST, port=app_settings.PORT, reload=app_settings.DEBUG)
