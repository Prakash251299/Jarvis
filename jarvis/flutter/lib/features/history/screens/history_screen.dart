import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:intl/intl.dart';
import '../providers/history_provider.dart';

class HistoryScreen extends ConsumerWidget {
  const HistoryScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final historyAsync = ref.watch(historyProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Conversations'),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: () => ref.read(historyProvider.notifier).loadHistory(),
          ),
        ],
      ),
      body: historyAsync.when(
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (err, _) => Center(child: Text('Failed to load history: $err')),
        data: (conversations) {
          if (conversations.isEmpty) {
            return const Center(child: Text('No previous conversations.'));
          }

          return ListView.separated(
            itemCount: conversations.length,
            separatorBuilder: (context, index) => const Divider(height: 1),
            itemBuilder: (context, index) {
              final item = conversations[index];
              final dateStr = DateFormat.yMMMd().add_jm().format(item.updatedAt);

              return ListTile(
                leading: const Icon(Icons.chat_bubble_outline),
                title: Text(
                  item.title,
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                  style: const TextStyle(fontWeight: FontWeight.w500),
                ),
                subtitle: Text(
                  '$dateStr • ${item.messageCount} messages',
                  style: const TextStyle(fontSize: 12, color: Colors.grey),
                ),
                trailing: IconButton(
                  icon: const Icon(Icons.delete_outline, size: 20, color: Colors.redAccent),
                  onPressed: () {
                    ref.read(historyProvider.notifier).deleteConversation(item.id);
                  },
                ),
                onTap: () {
                  context.go('/chat/${item.id}');
                },
              );
            },
          );
        },
      ),
    );
  }
}
