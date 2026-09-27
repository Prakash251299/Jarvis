import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:uuid/uuid.dart';

import '../../../core/constants/colors.dart';
import '../../../widgets/avatar_widget.dart';
import '../providers/chat_provider.dart';
import '../widgets/message_bubble.dart';
import '../widgets/message_input.dart';
import '../widgets/typing_indicator.dart';
import '../../settings/providers/settings_provider.dart';

class ChatScreen extends ConsumerStatefulWidget {
  final String conversationId;

  const ChatScreen({super.key, required this.conversationId});

  @override
  ConsumerState<ChatScreen> createState() => _ChatScreenState();
}

class _ChatScreenState extends ConsumerState<ChatScreen> {
  final ScrollController _scrollController = ScrollController();

  @override
  void dispose() {
    _scrollController.dispose();
    super.dispose();
  }

  void _scrollToBottom() {
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (_scrollController.hasClients) {
        _scrollController.animateTo(
          _scrollController.position.maxScrollExtent,
          duration: const Duration(milliseconds: 250),
          curve: Curves.easeOut,
        );
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    final chatState = ref.watch(chatProvider(widget.conversationId));
    final settings = ref.watch(settingsProvider);

    ref.listen(chatProvider(widget.conversationId), (previous, next) {
      if (previous?.messages.length != next.messages.length || next.isStreaming) {
        _scrollToBottom();
      }
    });

    return Scaffold(
      appBar: AppBar(
        title: Row(
          children: [
            const JarvisAvatar(size: 28),
            const SizedBox(width: 8),
            Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text('Jarvis', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16)),
                Text(
                  settings.model,
                  style: const TextStyle(fontSize: 11, color: Colors.grey),
                ),
              ],
            ),
          ],
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.add),
            tooltip: 'New conversation',
            onPressed: () {
              final newId = const Uuid().v4();
              context.go('/chat/$newId');
            },
          ),
          IconButton(
            icon: const Icon(Icons.history),
            tooltip: 'History',
            onPressed: () => context.push('/history'),
          ),
          IconButton(
            icon: const Icon(Icons.settings),
            tooltip: 'Settings',
            onPressed: () => context.push('/settings'),
          ),
        ],
      ),
      body: Column(
        children: [
          if (chatState.errorMessage != null)
            Container(
              width: double.infinity,
              color: AppColors.recordingRed.withValues(alpha: 0.1),
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
              child: Row(
                children: [
                  const Icon(Icons.error_outline, color: AppColors.recordingRed, size: 18),
                  const SizedBox(width: 8),
                  Expanded(
                    child: Text(
                      chatState.errorMessage!,
                      style: const TextStyle(color: AppColors.recordingRed, fontSize: 13),
                    ),
                  ),
                ],
              ),
            ),
          Expanded(
            child: chatState.isLoading
                ? const Center(child: CircularProgressIndicator())
                : chatState.messages.isEmpty
                    ? Center(
                        child: Column(
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: [
                            const JarvisAvatar(size: 64),
                            const SizedBox(height: 16),
                            Text(
                              'How can I help you today?',
                              style: Theme.of(context).textTheme.titleLarge,
                            ),
                            const SizedBox(height: 8),
                            const Text(
                              'All intelligence runs 100% locally on your machine.',
                              style: TextStyle(color: Colors.grey),
                            ),
                          ],
                        ),
                      )
                    : ListView.builder(
                        controller: _scrollController,
                        padding: const EdgeInsets.symmetric(vertical: 16),
                        itemCount: chatState.messages.length,
                        itemBuilder: (context, index) {
                          return MessageBubble(message: chatState.messages[index]);
                        },
                      ),
          ),
          if (chatState.statusMessage != null)
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 4),
              child: Row(
                children: [
                  const TypingIndicator(),
                  const SizedBox(width: 8),
                  Text(
                    chatState.statusMessage!,
                    style: TextStyle(
                      fontSize: 12,
                      color: Theme.of(context).colorScheme.onSurface.withValues(alpha: 0.6),
                    ),
                  ),
                ],
              ),
            ),
          MessageInput(conversationId: widget.conversationId),
        ],
      ),
    );
  }
}
