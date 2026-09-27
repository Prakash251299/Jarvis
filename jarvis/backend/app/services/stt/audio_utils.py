from __future__ import annotations

import io
import shutil
import struct
import subprocess
from typing import Tuple
from loguru import logger

WAV_HEADER_RIFF = b"RIFF"
WAV_HEADER_WAVE = b"WAVE"
MIN_AUDIO_BYTES = 16

def is_ffmpeg_available() -> bool:
    return shutil.which("ffmpeg") is not None

def convert_to_wav(
    audio_bytes: bytes,
    source_format: str = "auto",
    sample_rate: int = 16000,
    channels: int = 1,
) -> bytes:
    """
    Convert audio bytes (e.g. WebM, Opus, MP3, Ogg, M4A) to 16kHz mono 16-bit PCM WAV.
    """
    if is_wav(audio_bytes):
        sr, ch = parse_wav_params(audio_bytes)
        if sr == sample_rate and ch == channels:
            return audio_bytes

    if not is_ffmpeg_available():
        logger.warning("ffmpeg is not installed on system PATH. Attempting soundfile fallback.")
        return convert_with_soundfile(audio_bytes, sample_rate, channels)

    cmd = [
        "ffmpeg",
        "-hide_banner",
        "-loglevel", "error",
        "-y",
    ]
    if source_format and source_format != "auto":
        cmd.extend(["-f", source_format])

    cmd.extend([
        "-i", "pipe:0",
        "-ar", str(sample_rate),
        "-ac", str(channels),
        "-f", "wav",
        "-acodec", "pcm_s16le",
        "pipe:1",
    ])

    try:
        proc = subprocess.run(
            cmd,
            input=audio_bytes,
            capture_output=True,
            check=True,
            timeout=30,
        )
        return proc.stdout
    except subprocess.CalledProcessError as e:
        stderr_text = e.stderr.decode(errors="replace")
        logger.error("ffmpeg conversion failed: {}", stderr_text)
        raise RuntimeError(f"Audio conversion failed: {stderr_text}") from e
    except subprocess.TimeoutExpired as e:
        logger.error("ffmpeg conversion timed out after 30s")
        raise RuntimeError("Audio conversion timed out") from e

def convert_with_soundfile(audio_bytes: bytes, sample_rate: int, channels: int) -> bytes:
    try:
        import soundfile as sf
        import numpy as np

        buf_in = io.BytesIO(audio_bytes)
        data, sr = sf.read(buf_in, dtype="int16", always_2d=True)

        if sr != sample_rate:
            # Resample linearly
            num_samples = int(len(data) * sample_rate / sr)
            indices = (np.arange(num_samples) * (len(data) / num_samples)).astype(int)
            data = data[indices]

        if channels == 1 and data.shape[1] > 1:
            data = data.mean(axis=1, keepdims=True).astype(np.int16)

        buf_out = io.BytesIO()
        sf.write(buf_out, data, sample_rate, format="WAV", subtype="PCM_16")
        return buf_out.getvalue()
    except Exception as e:
        raise RuntimeError(f"Audio conversion without ffmpeg failed: {e}") from e

def is_wav(data: bytes) -> bool:
    return len(data) >= 12 and data[:4] == WAV_HEADER_RIFF and data[8:12] == WAV_HEADER_WAVE

def parse_wav_params(data: bytes) -> Tuple[int, int]:
    try:
        channels = struct.unpack_from("<H", data, 22)[0]
        sample_rate = struct.unpack_from("<I", data, 24)[0]
        return sample_rate, channels
    except Exception:
        return 0, 0

def get_audio_duration(audio_bytes: bytes) -> float:
    if is_wav(audio_bytes):
        try:
            byte_rate = struct.unpack_from("<I", audio_bytes, 28)[0]
            idx = audio_bytes.find(b"data", 36)
            if idx != -1 and byte_rate > 0:
                data_size = struct.unpack_from("<I", audio_bytes, idx + 4)[0]
                return round(data_size / byte_rate, 2)
        except Exception:
            pass
    return 0.0

def validate_audio(audio_bytes: bytes) -> bool:
    if not audio_bytes or len(audio_bytes) < MIN_AUDIO_BYTES:
        return False
    # Check known audio signatures (RIFF for wav, ID3 / FFFB for mp3, OggS, WebM / EBML)
    signatures = [
        b"RIFF",
        b"ID3",
        b"\xff\xfb",
        b"\xff\xf3",
        b"\xff\xf2",
        b"OggS",
        b"fLaC",
        b"\x1a\x45\xdf\xa3",
    ]
    header = audio_bytes[:4]
    for sig in signatures:
        if header.startswith(sig[:len(header)]):
            return True
    if len(audio_bytes) > 12 and audio_bytes[4:8] in (b"ftyp", b"moov", b"mdat"):
        return True
    return False
