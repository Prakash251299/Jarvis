from __future__ import annotations

import asyncio
import io
import threading
import time
from dataclasses import dataclass, field
from typing import List, Optional
from loguru import logger
from app.config import get_settings
from app.services.stt.audio_utils import convert_to_wav, get_audio_duration

@dataclass
class TranscriptionSegment:
    start: float
    end: float
    text: str

@dataclass
class TranscriptionResult:
    text: str
    language: str
    duration: float
    segments: List[TranscriptionSegment] = field(default_factory=list)
    model_size: str = ""

class WhisperService:
    """Faster-Whisper Speech-to-Text service with lazy initialization and threadpool isolation."""

    _instance: Optional["WhisperService"] = None
    _lock = threading.Lock()

    def __new__(cls) -> "WhisperService":
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._model = None
                    cls._instance._init_lock = threading.Lock()
        return cls._instance

    def __init__(self):
        self.settings = get_settings()

    def _get_or_load_model(self):
        if self._model is not None:
            return self._model

        with self._init_lock:
            if self._model is not None:
                return self._model

            model_size = self.settings.WHISPER_MODEL
            device = self.settings.WHISPER_DEVICE
            compute_type = self.settings.WHISPER_COMPUTE_TYPE

            logger.info("Initializing Faster-Whisper model '{}' on device '{}' with compute_type '{}'...", model_size, device, compute_type)
            start_time = time.monotonic()
            try:
                from faster_whisper import WhisperModel
                self._model = WhisperModel(model_size, device=device, compute_type=compute_type)
                logger.info("Faster-Whisper model '{}' loaded in {:.2f}s", model_size, time.monotonic() - start_time)
            except Exception as e:
                logger.error("Failed to load Faster-Whisper model: {}", e)
                raise RuntimeError(f"Failed to load Faster-Whisper model: {e}") from e

            return self._model

    def _transcribe_sync(self, audio_bytes: bytes, language: Optional[str] = None) -> TranscriptionResult:
        model = self._get_or_load_model()
        wav_bytes = convert_to_wav(audio_bytes)
        duration = get_audio_duration(wav_bytes)

        wav_io = io.BytesIO(wav_bytes)
        lang = language if language and language != "auto" else None

        segments_gen, info = model.transcribe(
            wav_io,
            language=lang,
            beam_size=5,
            vad_filter=True,
            vad_parameters=dict(min_silence_duration_ms=400),
        )

        segments: List[TranscriptionSegment] = []
        text_parts: List[str] = []

        for seg in segments_gen:
            cleaned = seg.text.strip()
            if cleaned:
                text_parts.append(cleaned)
                segments.append(TranscriptionSegment(start=seg.start, end=seg.end, text=cleaned))

        detected_lang = info.language if info else (language or "en")
        full_text = " ".join(text_parts).strip()

        logger.debug("Transcribed speech: '{}' (duration: {:.2f}s, language: {})", full_text, duration, detected_lang)

        return TranscriptionResult(
            text=full_text,
            language=detected_lang,
            duration=duration,
            segments=segments,
            model_size=self.settings.WHISPER_MODEL,
        )

    async def transcribe(self, audio_bytes: bytes, language: Optional[str] = None) -> TranscriptionResult:
        if not audio_bytes:
            return TranscriptionResult(text="", language="en", duration=0.0)

        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, self._transcribe_sync, audio_bytes, language)

    async def health_check(self) -> bool:
        try:
            loop = asyncio.get_running_loop()
            await loop.run_in_executor(None, self._get_or_load_model)
            return True
        except Exception:
            return False

whisper_service = WhisperService()
