import '../../../core/constants/app_constants.dart';

class SettingsModel {
  final String model;
  final String whisperModel;
  final String piperVoice;
  final bool voiceOutputEnabled;
  final bool memoryEnabled;

  const SettingsModel({
    this.model = AppConstants.defaultModel,
    this.whisperModel = AppConstants.defaultWhisperModel,
    this.piperVoice = AppConstants.defaultPiperVoice,
    this.voiceOutputEnabled = true,
    this.memoryEnabled = true,
  });

  SettingsModel copyWith({
    String? model,
    String? whisperModel,
    String? piperVoice,
    bool? voiceOutputEnabled,
    bool? memoryEnabled,
  }) {
    return SettingsModel(
      model: model ?? this.model,
      whisperModel: whisperModel ?? this.whisperModel,
      piperVoice: piperVoice ?? this.piperVoice,
      voiceOutputEnabled: voiceOutputEnabled ?? this.voiceOutputEnabled,
      memoryEnabled: memoryEnabled ?? this.memoryEnabled,
    );
  }

  factory SettingsModel.fromJson(Map<String, dynamic> json) {
    return SettingsModel(
      model: json['model'] as String? ?? AppConstants.defaultModel,
      whisperModel: json['whisper_model'] as String? ?? AppConstants.defaultWhisperModel,
      piperVoice: json['piper_voice'] as String? ?? AppConstants.defaultPiperVoice,
      voiceOutputEnabled: json['voice_output_enabled'] as bool? ?? true,
      memoryEnabled: json['memory_enabled'] as bool? ?? true,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'model': model,
      'whisper_model': whisperModel,
      'piper_voice': piperVoice,
      'voice_output_enabled': voiceOutputEnabled,
      'memory_enabled': memoryEnabled,
    };
  }
}
