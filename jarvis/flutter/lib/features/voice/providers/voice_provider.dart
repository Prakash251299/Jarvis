import 'dart:typed_data';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../core/di/injection_container.dart';
import '../../chat/providers/chat_provider.dart';

class VoiceState {
  final bool isRecording;
  final bool isProcessing;
  final double audioLevel;
  final String? error;

  const VoiceState({
    this.isRecording = false,
    this.isProcessing = false,
    this.audioLevel = 0.0,
    this.error,
  });

  VoiceState copyWith({
    bool? isRecording,
    bool? isProcessing,
    double? audioLevel,
    String? error,
  }) {
    return VoiceState(
      isRecording: isRecording ?? this.isRecording,
      isProcessing: isProcessing ?? this.isProcessing,
      audioLevel: audioLevel ?? this.audioLevel,
      error: error,
    );
  }
}

class VoiceNotifier extends StateNotifier<VoiceState> {
  final Ref _ref;

  VoiceNotifier(this._ref) : super(const VoiceState()) {
    _ref.read(audioServiceProvider).waveformStream.listen((lvl) {
      if (state.isRecording) {
        state = state.copyWith(audioLevel: lvl);
      }
    });
  }

  Future<void> startRecording() async {
    try {
      // Stop assistant speech on user interrupt
      await _ref.read(audioServiceProvider).stopAudio();
      await _ref.read(audioServiceProvider).startRecording();
      state = state.copyWith(isRecording: true, audioLevel: 0.0, error: null);
    } catch (e) {
      state = state.copyWith(error: 'Could not access microphone');
    }
  }

  Future<void> stopRecording(String currentConvId) async {
    if (!state.isRecording) return;
    state = state.copyWith(isRecording: false, isProcessing: true);

    try {
      final Uint8List? audioBytes = await _ref.read(audioServiceProvider).stopRecording();
      if (audioBytes != null && audioBytes.isNotEmpty) {
        final text = await _ref.read(apiServiceProvider).transcribeAudio(audioBytes);
        if (text.trim().isNotEmpty) {
          _ref.read(chatProvider(currentConvId).notifier).sendMessage(text);
        }
      }
    } catch (e) {
      state = state.copyWith(error: 'Transcription failed');
    } finally {
      state = state.copyWith(isProcessing: false, audioLevel: 0.0);
    }
  }
}

final voiceProvider = StateNotifierProvider<VoiceNotifier, VoiceState>((ref) {
  return VoiceNotifier(ref);
});
