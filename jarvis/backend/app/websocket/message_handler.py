from __future__ import annotations

import asyncio
import base64
from typing import Dict, List, Optional
import aiosqlite
from loguru import logger

from app.websocket.events import EventType, WebSocketMessage
from app.websocket.connection_manager import ConnectionManager
from app.services.llm.chat_handler import chat_handler
from app.services.stt.whisper_service import whisper_service
from app.services.tts.piper_service import piper_service
from app.services.memory.memory_service import memory_service
from app.config import get_settings

class MessageHandler:
    """Handles parsing, audio buffering, speech recognition, LLM streaming, and TTS dispatch for WebSockets."""

    def __init__(self):
        self.settings = get_settings()
        self._audio_buffers: Dict[str, List[bytes]] = {}
        self._active_cancellations: Dict[str, asyncio.Event] = {}

    def _get_audio_buffer(self, conversation_id: str) -> List[bytes]:
        if conversation_id not in self._audio_buffers:
            self._audio_buffers[conversation_id] = []
        return self._audio_buffers[conversation_id]

    def _clear_audio_buffer(self, conversation_id: str):
        if conversation_id in self._audio_buffers:
            self._audio_buffers[conversation_id].clear()

    async def handle_audio_chunk(self, conversation_id: str, chunk: bytes):
        buffer = self._get_audio_buffer(conversation_id)
        buffer.append(chunk)

    async def handle_audio_end(
        self,
        conversation_id: str,
        manager: ConnectionManager,
        conn: aiosqlite.Connection,
    ):
        buffer = self._get_audio_buffer(conversation_id)
        if not buffer:
            return

        combined_audio = b"".join(buffer)
        self._clear_audio_buffer(conversation_id)

        await manager.send_json(conversation_id, {
            "event": EventType.STATUS,
            "data": "Transcribing audio..."
        })

        try:
            transcription = await whisper_service.transcribe(combined_audio)
            user_text = transcription.text.strip()
            if not user_text:
                await manager.send_json(conversation_id, {
                    "event": EventType.ERROR,
                    "data": "No speech detected."
                })
                return

            await manager.send_json(conversation_id, {
                "event": EventType.TRANSCRIPTION,
                "data": {
                    "text": user_text,
                    "language": transcription.language,
                    "duration": transcription.duration,
                }
            })

            await self.handle_text_message(conversation_id, user_text, manager, conn, is_voice=True)
        except Exception as e:
            logger.error("Audio processing failed for {}: {}", conversation_id, e)
            await manager.send_json(conversation_id, {
                "event": EventType.ERROR,
                "data": f"Speech processing error: {e}"
            })

    async def handle_cancel_generation(self, conversation_id: str, manager: ConnectionManager):
        if conversation_id in self._active_cancellations:
            self._active_cancellations[conversation_id].set()
            logger.info("Generation cancellation signaled for conversation: {}", conversation_id)
            await manager.send_json(conversation_id, {
                "event": EventType.STATUS,
                "data": "Generation interrupted."
            })

    async def handle_text_message(
        self,
        conversation_id: str,
        text: str,
        manager: ConnectionManager,
        conn: aiosqlite.Connection,
        is_voice: bool = False,
    ):
        cancel_event = asyncio.Event()
        self._active_cancellations[conversation_id] = cancel_event

        await manager.send_json(conversation_id, {
            "event": EventType.GENERATION_START,
            "data": {"user_message": text}
        })

        accumulated_response: List[str] = []
        try:
            # Check user settings
            cursor = await conn.execute("SELECT value FROM settings WHERE key = 'voice_output_enabled';")
            row = await cursor.fetchone()
            voice_enabled = (row["value"].lower() == "true") if row else True

            async for token in chat_handler.stream_response(conn, conversation_id, text):
                if cancel_event.is_set():
                    logger.info("Chat generation cancelled mid-stream for {}", conversation_id)
                    break

                accumulated_response.append(token)
                await manager.send_json(conversation_id, {
                    "event": EventType.TOKEN,
                    "data": token
                })

            full_reply = "".join(accumulated_response).strip()

            await manager.send_json(conversation_id, {
                "event": EventType.GENERATION_END,
                "data": {"content": full_reply}
            })

            # Auto-extract long term memory
            asyncio.create_task(memory_service.extract_and_save_memories(conn, conversation_id, text))

            # If voice mode is requested and voice is enabled, synthesize and send speech
            if (is_voice or voice_enabled) and full_reply and not cancel_event.is_set():
                await manager.send_json(conversation_id, {
                    "event": EventType.STATUS,
                    "data": "Synthesizing voice..."
                })
                try:
                    wav_bytes = await piper_service.synthesize(full_reply)
                    if wav_bytes:
                        b64_audio = base64.b64encode(wav_bytes).decode("ascii")
                        await manager.send_json(conversation_id, {
                            "event": EventType.AUDIO_RESPONSE,
                            "data": {
                                "audio_base64": b64_audio,
                                "format": "wav",
                            }
                        })
                except Exception as tts_err:
                    logger.warning("TTS synthesis failed for response: {}", tts_err)

        except Exception as e:
            logger.error("Chat generation failed for {}: {}", conversation_id, e)
            await manager.send_json(conversation_id, {
                "event": EventType.ERROR,
                "data": str(e)
            })
        finally:
            self._active_cancellations.pop(conversation_id, None)

message_handler = MessageHandler()
