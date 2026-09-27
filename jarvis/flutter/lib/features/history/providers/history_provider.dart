import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../core/di/injection_container.dart';
import '../../chat/models/conversation_model.dart';

class HistoryNotifier extends StateNotifier<AsyncValue<List<ConversationModel>>> {
  final Ref _ref;

  HistoryNotifier(this._ref) : super(const AsyncValue.loading()) {
    loadHistory();
  }

  Future<void> loadHistory() async {
    state = const AsyncValue.loading();
    try {
      final conversations = await _ref.read(apiServiceProvider).listConversations();
      state = AsyncValue.data(conversations);
    } catch (e, st) {
      state = AsyncValue.error(e, st);
    }
  }

  Future<void> deleteConversation(String id) async {
    try {
      await _ref.read(apiServiceProvider).deleteConversation(id);
      state.whenData((list) {
        state = AsyncValue.data(list.where((c) => c.id != id).toList());
      });
    } catch (_) {}
  }
}

final historyProvider = StateNotifierProvider<HistoryNotifier, AsyncValue<List<ConversationModel>>>((ref) {
  return HistoryNotifier(ref);
});
