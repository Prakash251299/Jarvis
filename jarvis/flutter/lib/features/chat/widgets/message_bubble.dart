import 'package:flutter/material.dart';
import '../../../core/constants/colors.dart';
import '../../../widgets/avatar_widget.dart';
import '../../../widgets/markdown_renderer.dart';
import '../models/message_model.dart';

class MessageBubble extends StatelessWidget {
  final MessageModel message;

  const MessageBubble({super.key, required this.message});

  @override
  Widget build(BuildContext context) {
    final isUser = message.isUser;
    final isDark = Theme.of(context).brightness == Brightness.dark;

    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8, horizontal: 16),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        mainAxisAlignment: isUser ? MainAxisAlignment.end : MainAxisAlignment.start,
        children: [
          if (!isUser) ...[
            JarvisAvatar(isPulsing: message.isStreaming),
            const SizedBox(width: 12),
          ],
          Flexible(
            child: Container(
              constraints: const BoxConstraints(maxWidth: 720),
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
              decoration: BoxDecoration(
                color: isUser
                    ? (isDark ? AppColors.userBubbleDark : AppColors.userBubbleLight)
                    : (isDark ? AppColors.assistantBubbleDark : AppColors.assistantBubbleLight),
                borderRadius: BorderRadius.circular(16).copyWith(
                  bottomRight: isUser ? const Radius.circular(4) : null,
                  bottomLeft: !isUser ? const Radius.circular(4) : null,
                ),
                border: !isUser && !isDark ? Border.all(color: Colors.black12) : null,
              ),
              child: isUser
                  ? SelectableText(
                      message.content,
                      style: const TextStyle(color: Colors.white, fontSize: 15, height: 1.4),
                    )
                  : MarkdownRenderer(
                      content: message.content,
                      isStreaming: message.isStreaming,
                    ),
            ),
          ),
          if (isUser) ...[
            const SizedBox(width: 12),
            const UserAvatar(),
          ],
        ],
      ),
    );
  }
}
