class AppConstants {
  AppConstants._();

  static const String appName = 'Jarvis';
  static const String backendBaseUrl = 'http://localhost:8000';
  static const String wsBaseUrl = 'ws://localhost:8000';
  static const String apiVersion = '/api/v1';

  static const Duration wsReconnectDelay = Duration(seconds: 3);
  static const int wsMaxReconnectAttempts = 5;

  static const int audioSampleRate = 16000;
  static const int audioChannels = 1;

  static const double maxChatWidth = 840.0;
  static const Duration animationFast = Duration(milliseconds: 200);
  static const Duration animationNormal = Duration(milliseconds: 350);

  // Storage keys
  static const String keySelectedModel = 'selected_model';
  static const String keyVoiceEnabled = 'voice_enabled';
  static const String keyMemoryEnabled = 'memory_enabled';
  static const String keyWhisperModel = 'whisper_model';
  static const String keyPiperVoice = 'piper_voice';
  static const String keyLastConversationId = 'last_conversation_id';

  // Defaults
  static const String defaultModel = 'qwen3:8b';
  static const String defaultWhisperModel = 'base';
  static const String defaultPiperVoice = 'en_US-lessac-medium';
}
