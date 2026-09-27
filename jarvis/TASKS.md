# JARVIS – Local AI Voice Assistant: Task List

## Phase 1: Architecture & Foundation
- [x] Create TASKS.md
- [x] Create PROGRESS.md
- [x] Create full folder structure (backend + flutter)
- [x] Create database schema (SQLite)
- [x] Create README.md
- [x] Create .env.example
- [x] Create docker-compose.yml
- [x] Create setup scripts (setup.sh)

## Phase 2: Backend Foundation
- [x] backend/requirements.txt
- [x] backend/app/__init__.py
- [x] backend/app/main.py
- [x] backend/app/config.py
- [x] backend/app/database/connection.py
- [x] backend/app/database/migrations.py
- [x] backend/app/models/conversation.py
- [x] backend/app/models/message.py
- [x] backend/app/models/memory_entry.py
- [x] backend/app/schemas/conversation.py
- [x] backend/app/schemas/message.py
- [x] backend/app/schemas/settings.py

## Phase 3: Ollama / LLM Integration
- [x] backend/app/services/llm/ollama_client.py
- [x] backend/app/services/llm/chat_handler.py
- [x] backend/app/services/llm/prompt_builder.py
- [x] backend/app/api/routes/llm.py

## Phase 4: Speech-to-Text (Faster-Whisper)
- [x] backend/app/services/stt/whisper_service.py
- [x] backend/app/services/stt/audio_utils.py
- [x] backend/app/api/routes/stt.py

## Phase 5: Text-to-Speech (Piper)
- [x] backend/app/services/tts/piper_service.py
- [x] backend/app/services/tts/audio_stream.py
- [x] backend/app/api/routes/tts.py

## Phase 6: Memory System
- [x] backend/app/services/memory/memory_service.py
- [x] backend/app/services/memory/context_retriever.py
- [x] backend/app/api/routes/memory.py

## Phase 7: WebSocket Hub
- [x] backend/app/websocket/connection_manager.py
- [x] backend/app/websocket/message_handler.py
- [x] backend/app/websocket/events.py
- [x] backend/app/api/routes/ws.py

## Phase 8: Plugin / Tool Framework
- [x] backend/app/tools/base_tool.py
- [x] backend/app/tools/tool_registry.py
- [x] backend/app/tools/builtin/calculator.py
- [x] backend/app/tools/builtin/datetime_tool.py

## Phase 9: Flutter App – Core
- [x] flutter/pubspec.yaml
- [x] flutter/lib/main.dart
- [x] flutter/lib/core/constants/app_constants.dart
- [x] flutter/lib/core/constants/colors.dart
- [x] flutter/lib/core/theme/app_theme.dart
- [x] flutter/lib/core/router/app_router.dart
- [x] flutter/lib/core/di/injection_container.dart
- [x] flutter/lib/services/websocket_service.dart
- [x] flutter/lib/services/audio_service.dart
- [x] flutter/lib/services/api_service.dart

## Phase 10: Flutter App – Features
- [x] flutter/lib/features/chat/models/message_model.dart
- [x] flutter/lib/features/chat/models/conversation_model.dart
- [x] flutter/lib/features/chat/providers/chat_provider.dart
- [x] flutter/lib/features/chat/screens/chat_screen.dart
- [x] flutter/lib/features/chat/widgets/message_bubble.dart
- [x] flutter/lib/features/chat/widgets/message_input.dart
- [x] flutter/lib/features/chat/widgets/typing_indicator.dart
- [x] flutter/lib/features/chat/widgets/waveform_animation.dart
- [x] flutter/lib/features/voice/providers/voice_provider.dart
- [x] flutter/lib/features/voice/widgets/mic_button.dart
- [x] flutter/lib/features/settings/models/settings_model.dart
- [x] flutter/lib/features/settings/providers/settings_provider.dart
- [x] flutter/lib/features/settings/screens/settings_screen.dart
- [x] flutter/lib/features/history/screens/history_screen.dart
- [x] flutter/lib/features/history/providers/history_provider.dart
- [x] flutter/lib/widgets/markdown_renderer.dart
- [x] flutter/lib/widgets/code_block.dart
- [x] flutter/lib/widgets/avatar_widget.dart

## Phase 11: Testing & Verification
- [x] backend/pytest.ini
- [x] backend/tests/test_api.py
- [x] Timezone deprecation fixes (Python 3.12+ datetime.now(timezone.utc))
- [x] flutter/test/models_test.dart
- [x] Static analysis (flutter analyze: 0 issues)

