import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../core/di/injection_container.dart';
import '../models/settings_model.dart';

class SettingsNotifier extends StateNotifier<SettingsModel> {
  final Ref _ref;

  SettingsNotifier(this._ref) : super(const SettingsModel()) {
    loadSettings();
  }

  Future<void> loadSettings() async {
    try {
      final settings = await _ref.read(apiServiceProvider).getSettings();
      state = settings;
    } catch (_) {}
  }

  Future<void> updateModel(String model) async {
    state = state.copyWith(model: model);
    await _sync();
  }

  Future<void> toggleVoice(bool enabled) async {
    state = state.copyWith(voiceOutputEnabled: enabled);
    await _sync();
  }

  Future<void> toggleMemory(bool enabled) async {
    state = state.copyWith(memoryEnabled: enabled);
    await _sync();
  }

  Future<void> updateWhisperModel(String model) async {
    state = state.copyWith(whisperModel: model);
    await _sync();
  }

  Future<void> updatePiperVoice(String voice) async {
    state = state.copyWith(piperVoice: voice);
    await _sync();
  }

  Future<void> _sync() async {
    try {
      final updated = await _ref.read(apiServiceProvider).updateSettings(state);
      state = updated;
    } catch (_) {}
  }
}

final settingsProvider = StateNotifierProvider<SettingsNotifier, SettingsModel>((ref) {
  return SettingsNotifier(ref);
});

final availableModelsProvider = FutureProvider<List<String>>((ref) async {
  return await ref.read(apiServiceProvider).getAvailableModels();
});
