import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../core/constants/colors.dart';
import '../providers/chat_provider.dart';
import '../../voice/providers/voice_provider.dart';
import '../../voice/widgets/mic_button.dart';
import 'waveform_animation.dart';

class MessageInput extends ConsumerStatefulWidget {
  final String conversationId;

  const MessageInput({super.key, required this.conversationId});

  @override
  ConsumerState<MessageInput> createState() => _MessageInputState();
}

class _MessageInputState extends ConsumerState<MessageInput> {
  final TextEditingController _controller = TextEditingController();
  final FocusNode _focusNode = FocusNode();

  @override
  void dispose() {
    _controller.dispose();
    _focusNode.dispose();
    super.dispose();
  }

  void _handleSend() {
    final text = _controller.text.trim();
    if (text.isEmpty) return;
    ref.read(chatProvider(widget.conversationId).notifier).sendMessage(text);
    _controller.clear();
  }

  @override
  Widget build(BuildContext context) {
    final chatState = ref.watch(chatProvider(widget.conversationId));
    final voiceState = ref.watch(voiceProvider);
    final isDark = Theme.of(context).brightness == Brightness.dark;

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      decoration: BoxDecoration(
        color: isDark ? AppColors.surfaceDark : Colors.white,
        border: Border(top: BorderSide(color: isDark ? Colors.white10 : Colors.black12)),
      ),
      child: SafeArea(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            if (voiceState.isRecording) ...[
              Padding(
                padding: const EdgeInsets.symmetric(vertical: 4),
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    const Text(
                      'Recording... Hold to speak',
                      style: TextStyle(color: AppColors.recordingRed, fontWeight: FontWeight.bold),
                    ),
                    const SizedBox(width: 8),
                    WaveformAnimation(level: voiceState.audioLevel),
                  ],
                ),
              ),
            ],
            if (chatState.statusMessage != null) ...[
              Padding(
                padding: const EdgeInsets.only(bottom: 6),
                child: Text(
                  chatState.statusMessage!,
                  style: TextStyle(
                    fontSize: 12,
                    color: Theme.of(context).colorScheme.primary,
                    fontStyle: FontStyle.italic,
                  ),
                ),
              ),
            ],
            Row(
              children: [
                Expanded(
                  child: Container(
                    decoration: BoxDecoration(
                      color: isDark ? AppColors.surfaceVariantDark : AppColors.surfaceVariantLight,
                      borderRadius: BorderRadius.circular(24),
                    ),
                    child: TextField(
                      controller: _controller,
                      focusNode: _focusNode,
                      maxLines: 4,
                      minLines: 1,
                      textInputAction: TextInputAction.send,
                      onSubmitted: (_) => _handleSend(),
                      decoration: const InputDecoration(
                        hintText: 'Message Jarvis...',
                        border: InputBorder.none,
                        contentPadding: EdgeInsets.symmetric(horizontal: 18, vertical: 12),
                      ),
                    ),
                  ),
                ),
                const SizedBox(width: 8),
                if (chatState.isStreaming)
                  IconButton(
                    onPressed: () {
                      ref.read(chatProvider(widget.conversationId).notifier).cancelCurrentResponse();
                    },
                    icon: const Icon(Icons.stop_circle, color: AppColors.recordingRed, size: 36),
                    tooltip: 'Stop generation',
                  )
                else ...[
                  IconButton(
                    onPressed: _handleSend,
                    icon: const Icon(Icons.send_rounded, color: AppColors.primary, size: 28),
                    tooltip: 'Send message',
                  ),
                  const SizedBox(width: 4),
                  MicButton(conversationId: widget.conversationId),
                ],
              ],
            ),
          ],
        ),
      ),
    );
  }
}
