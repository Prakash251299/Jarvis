from __future__ import annotations

import asyncio
import io
import os
import shutil
import subprocess
import threading
from pathlib import Path
from typing import AsyncIterator, List, Optional
from loguru import logger
from app.config import get_settings
from app.services.tts.audio_stream import pcm_to_wav, sentence_splitter

class PiperService:
    """Local Text-to-Speech service utilizing Piper neural TTS engine with fallback support."""

    _instance: Optional["PiperService"] = None
    _lock = threading.Lock()

    def __new__(cls) -> "PiperService":
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        self.settings = get_settings()
        self.piper_bin = shutil.which("piper") or str(Path.home() / ".local/bin/piper")
        self.espeak_bin = shutil.which("espeak-ng") or shutil.which("espeak")
        self.data_dir = Path(self.settings.PIPER_DATA_DIR).expanduser()
        self._voice_cache: dict[str, Path] = {}

    def _find_voice_model(self, voice_name: str) -> Optional[Path]:
        if voice_name in self._voice_cache and self._voice_cache[voice_name].exists():
            return self._voice_cache[voice_name]

        if not self.data_dir.exists():
            return None

        candidates = [
            self.data_dir / f"{voice_name}.onnx",
            self.data_dir / voice_name / f"{voice_name}.onnx",
        ]
        for path in candidates:
            if path.exists():
                self._voice_cache[voice_name] = path
                return path

        # Glob search
        matches = list(self.data_dir.glob(f"**/{voice_name}*.onnx"))
        if matches:
            self._voice_cache[voice_name] = matches[0]
            return matches[0]

        # Any available onnx file in the directory
        all_models = list(self.data_dir.glob("**/*.onnx"))
        if all_models:
            self._voice_cache[voice_name] = all_models[0]
            return all_models[0]

        return None

    def list_voices(self) -> List[str]:
        if not self.data_dir.exists():
            return []
        return sorted(list({p.stem for p in self.data_dir.glob("**/*.onnx")}))

    def _synthesize_with_piper(self, text: str, voice_model_path: Optional[Path]) -> bytes:
        cmd = [self.piper_bin]
        if voice_model_path and voice_model_path.exists():
            cmd.extend(["--model", str(voice_model_path)])
        cmd.append("--output_raw")

        proc = subprocess.run(
            cmd,
            input=text.encode("utf-8"),
            capture_output=True,
            check=True,
            timeout=30,
        )
        raw_pcm = proc.stdout
        if not raw_pcm:
            raise RuntimeError("Piper produced empty audio output")

        return pcm_to_wav(raw_pcm, sample_rate=self.settings.PIPER_SAMPLE_RATE, channels=1)

    def _synthesize_with_espeak(self, text: str) -> bytes:
        if not self.espeak_bin:
            raise RuntimeError("Neither Piper nor espeak is available for TTS synthesis.")

        cmd = [self.espeak_bin, "--stdout", "-v", "en", text]
        proc = subprocess.run(cmd, capture_output=True, check=True, timeout=15)
        return proc.stdout

    def _synthesize_sync(self, text: str, voice: Optional[str] = None) -> bytes:
        cleaned_text = text.strip()
        if not cleaned_text:
            return b""

        target_voice = voice or self.settings.PIPER_VOICE
        voice_path = self._find_voice_model(target_voice)

        if Path(self.piper_bin).exists() or shutil.which("piper"):
            try:
                return self._synthesize_with_piper(cleaned_text, voice_path)
            except Exception as e:
                logger.warning("Piper synthesis failed, checking espeak fallback: {}", e)

        return self._synthesize_with_espeak(cleaned_text)

    async def synthesize(self, text: str, voice: Optional[str] = None) -> bytes:
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, self._synthesize_sync, text, voice)

    async def synthesize_streaming(self, text: str, voice: Optional[str] = None) -> AsyncIterator[bytes]:
        """Split text into sentence chunks and yield WAV audio per chunk for low-latency playback."""
        sentences = sentence_splitter(text)
        for sentence in sentences:
            if not sentence.strip():
                continue
            wav_chunk = await self.synthesize(sentence, voice=voice)
            if wav_chunk:
                yield wav_chunk

piper_service = PiperService()
