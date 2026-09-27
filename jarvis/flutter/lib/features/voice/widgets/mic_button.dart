import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../core/constants/colors.dart';
import '../providers/voice_provider.dart';

class MicButton extends ConsumerWidget {
  final String conversationId;

  const MicButton({super.key, required this.conversationId});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final voiceState = ref.watch(voiceProvider);

    return GestureDetector(
      onLongPressStart: (_) {
        ref.read(voiceProvider.notifier).startRecording();
      },
      onLongPressEnd: (_) {
        ref.read(voiceProvider.notifier).stopRecording(conversationId);
      },
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 200),
        width: 52,
        height: 52,
        decoration: BoxDecoration(
          shape: BoxShape.circle,
          color: voiceState.isRecording
              ? AppColors.recordingRed
              : (voiceState.isProcessing ? AppColors.warning : AppColors.primary),
          boxShadow: voiceState.isRecording
              ? [
                  BoxShadow(
                    color: AppColors.recordingRed.withValues(alpha: 0.5),
                    blurRadius: 16,
                    spreadRadius: 4,
                  )
                ]
              : null,
        ),
        child: Center(
          child: voiceState.isProcessing
              ? const SizedBox(
                  width: 24,
                  height: 24,
                  child: CircularProgressIndicator(strokeWidth: 2.5, color: Colors.white),
                )
              : Icon(
                  voiceState.isRecording ? Icons.mic : Icons.mic_none,
                  color: Colors.white,
                  size: 26,
                ),
        ),
      ),
    );
  }
}
