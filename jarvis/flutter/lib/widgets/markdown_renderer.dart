import 'package:flutter/material.dart';
import 'package:flutter_markdown/flutter_markdown.dart';

class MarkdownRenderer extends StatelessWidget {
  final String content;
  final bool isStreaming;

  const MarkdownRenderer({super.key, required this.content, this.isStreaming = false});

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final textStyle = theme.textTheme.bodyMedium?.copyWith(
      height: 1.6,
      fontSize: 15,
    );

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        MarkdownBody(
          data: content,
          selectable: true,
          styleSheet: MarkdownStyleSheet.fromTheme(theme).copyWith(
            p: textStyle,
            code: const TextStyle(
              fontFamily: 'monospace',
              fontSize: 13,
              backgroundColor: Color(0x22888888),
            ),
          ),
        ),
        if (isStreaming)
          Container(
            margin: const EdgeInsets.only(top: 4),
            width: 8,
            height: 16,
            color: theme.colorScheme.primary,
          ),
      ],
    );
  }
}
