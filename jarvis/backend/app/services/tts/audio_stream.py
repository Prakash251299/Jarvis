from __future__ import annotations

import io
import re
import wave
from typing import List

SENTENCE_SPLIT_REGEX = re.compile(r'(?<=[.!?])\s+(?=[A-Z0-9])|\n+')

def sentence_splitter(text: str) -> List[str]:
    """
    Split markdown / conversational text into speakable sentence chunks.
    Filters out empty lines and raw markdown delimiters.
    """
    # Remove markdown code blocks from speech stream or replace with label
    cleaned = re.sub(r'```[\s\S]*?```', ' [Code block provided in chat] ', text)
    cleaned = re.sub(r'`([^`]+)`', r'\1', cleaned)
    cleaned = re.sub(r'[*_#~]', '', cleaned)
    cleaned = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', cleaned) # links

    raw_chunks = SENTENCE_SPLIT_REGEX.split(cleaned.strip())
    sentences: List[str] = []
    current_buf: List[str] = []

    for chunk in raw_chunks:
        trimmed = chunk.strip()
        if not trimmed:
            continue
        current_buf.append(trimmed)
        combined = " ".join(current_buf)
        if len(combined) >= 40 or combined.endswith(('.', '!', '?')):
            sentences.append(combined)
            current_buf = []

    if current_buf:
        sentences.append(" ".join(current_buf))

    return sentences

def pcm_to_wav(pcm_data: bytes, sample_rate: int = 22050, channels: int = 1) -> bytes:
    """Pack raw 16-bit little-endian PCM bytes into standard RIFF WAV format."""
    buf = io.BytesIO()
    with wave.open(buf, 'wb') as wav_file:
        wav_file.setnchannels(channels)
        wav_file.setsampwidth(2) # 16 bits = 2 bytes
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(pcm_data)
    return buf.getvalue()
