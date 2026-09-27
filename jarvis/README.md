# JARVIS – 100% Local AI Voice Assistant

A ChatGPT-like voice assistant running completely on your local machine with **zero cloud APIs**, **zero external data transmission**, and **near real-time latency**.

---

## 🏛 Architecture Overview

```mermaid
graph TD
    subgraph Frontend [Flutter UI - Mobile / Desktop]
        A[Push-to-Talk Mic] --> B[AudioService]
        B --> C[WebSocket Channel / REST]
        D[ChatScreen] <--> E[ChatNotifier / Riverpod]
        E <--> C
        F[Audio Player] <-- C
    end

    subgraph Backend [FastAPI Server - Python 3.12+]
        C <--> G[WebSocket Hub / MessageHandler]
        G --> H[Faster-Whisper STT]
        G --> I[ChatHandler / PromptBuilder]
        I <--> J[Persistent Memory Engine]
        I <--> K[SQLite DB]
        I --> L[Ollama Local LLM: Qwen3 8B]
        L --> I
        I --> M[Piper Neural TTS]
        M --> G
    end

    subgraph Hardware [Local Compute]
        L --> GPU[Apple Silicon Metal / NVIDIA GPU / CPU]
        H --> CPU[CPU / Int8 Quantization]
    end
```

---

## 🚀 Key Features

1. **Voice Input (Push-To-Talk)**:
   - Hold the microphone button to record audio in 16kHz PCM WAV.
   - Streaming or batched transcription using **Faster-Whisper** (`int8` compute for high efficiency).
2. **ChatGPT-like Conversation Experience**:
   - Streaming LLM token-by-token output over WebSockets.
   - Markdown formatting with code block syntax highlighting and one-click copying.
   - Typing indicator and audio waveform reactivity.
3. **Voice Output with Interruption**:
   - Instant Text-To-Speech powered by **Piper**.
   - Automatic playback cancellation when the user speaks or hits stop.
4. **Persistent Long-Term Memory**:
   - SQLite schema storing messages, conversations, and distilled memory facts.
   - Automatic memory extraction for user preferences, notes, names, and locations.
5. **Settings & Customization**:
   - Live Ollama model switching (Qwen3 8B default).
   - Whisper model selection (`tiny`, `base`, `small`, `medium`).
   - Piper voice model switching and audio playback toggling.

---

## 🛠 Prerequisites

- **Python 3.12+**
- **Flutter 3.19+**
- **Ollama** installed: [ollama.com](https://ollama.com)
- **ffmpeg** installed (e.g. `brew install ffmpeg` on macOS)
- **Piper TTS** (automatically fetched by setup script or `brew install piper-tts`)

---

## ⚡ Quick Start

### 1. Run Automated Setup
```bash
./scripts/setup.sh
```

### 2. Manual Start

#### Terminal 1: Backend
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

#### Terminal 2: Flutter App
```bash
cd flutter
flutter pub get
flutter run -d macos  # or: flutter run -d chrome
```

---

## 🗄 Database Schema (SQLite)

- **`conversations`**: `id`, `title`, `created_at`, `updated_at`, `model_used`, `is_archived`
- **`messages`**: `id`, `conversation_id`, `role`, `content`, `timestamp`, `tokens_used`, `audio_path`
- **`memory_entries`**: `id`, `conversation_id`, `key`, `value`, `created_at`, `relevance_score`
- **`settings`**: `key`, `value`, `updated_at`

---

## 🔒 Privacy Guarantee

All LLM weights, speech recognition models, voice synthesis models, and conversation logs reside exclusively on your local storage. No analytics, tracking, or cloud proxies are present.
