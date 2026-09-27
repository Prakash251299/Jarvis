import 'dart:async';
import 'dart:convert';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:uuid/uuid.dart';
import '../../../core/di/injection_container.dart';
import '../models/message_model.dart';

class ChatState {
  final String conversationId;
  final List<MessageModel> messages;
  final bool isStreaming;
  final bool isLoading;
  final String? statusMessage;
  final String? errorMessage;

  const ChatState({
    required this.conversationId,
    this.messages = const [],
    this.isStreaming = false,
    this.isLoading = false,
    this.statusMessage,
    this.errorMessage,
  });

  ChatState copyWith({
    String? conversationId,
    List<MessageModel>? messages,
    bool? isStreaming,
    bool? isLoading,
    String? statusMessage,
    String? errorMessage,
  }) {
    return ChatState(
      conversationId: conversationId ?? this.conversationId,
      messages: messages ?? this.messages,
      isStreaming: isStreaming ?? this.isStreaming,
      isLoading: isLoading ?? this.isLoading,
      statusMessage: statusMessage,
      errorMessage: errorMessage,
    );
  }
}

class ChatNotifier extends StateNotifier<ChatState> {
  final Ref _ref;
  StreamSubscription? _wsSub;

  ChatNotifier(this._ref, String initialConvId)
      : super(ChatState(conversationId: initialConvId)) {
    _init(initialConvId);
  }

  void _init(String convId) {
    loadConversation(convId);
    _listenToWebSocket(convId);
  }

  void switchConversation(String newConvId) {
    _wsSub?.cancel();
    state = ChatState(conversationId: newConvId);
    _init(newConvId);
  }

  Future<void> loadConversation(String convId) async {
    state = state.copyWith(isLoading: true, errorMessage: null);
    try {
      final messages = await _ref.read(apiServiceProvider).getMessages(convId);
      state = state.copyWith(messages: messages, isLoading: false);
    } catch (e) {
      state = state.copyWith(isLoading: false, errorMessage: 'Failed to load conversation messages');
    }
  }

  void _listenToWebSocket(String convId) {
    final ws = _ref.read(webSocketServiceProvider);
    ws.connect(convId);

    _wsSub?.cancel();
    _wsSub = ws.eventStream.listen((event) {
      final type = event['event'] as String?;
      final data = event['data'];

      if (type == 'status') {
        state = state.copyWith(statusMessage: data as String?);
      } else if (type == 'generation_start') {
        state = state.copyWith(isStreaming: true, statusMessage: null);
        // Add pending assistant message
        final assistantMsg = MessageModel(
          id: const Uuid().v4(),
          conversationId: state.conversationId,
          role: MessageRole.assistant,
          content: '',
          timestamp: DateTime.now(),
          isStreaming: true,
        );
        state = state.copyWith(messages: [...state.messages, assistantMsg]);
      } else if (type == 'token') {
        final token = data as String? ?? '';
        if (state.messages.isNotEmpty && state.messages.last.isStreaming) {
          final last = state.messages.last;
          final updated = last.copyWith(content: last.content + token);
          final list = List<MessageModel>.from(state.messages);
          list[list.length - 1] = updated;
          state = state.copyWith(messages: list);
        }
      } else if (type == 'generation_end') {
        if (state.messages.isNotEmpty && state.messages.last.isStreaming) {
          final last = state.messages.last;
          final updated = last.copyWith(isStreaming: false);
          final list = List<MessageModel>.from(state.messages);
          list[list.length - 1] = updated;
          state = state.copyWith(messages: list, isStreaming: false, statusMessage: null);
        }
      } else if (type == 'audio_response') {
        final b64 = (data as Map<String, dynamic>?)?['audio_base64'] as String?;
        if (b64 != null) {
          final bytes = base64Decode(b64);
          _ref.read(audioServiceProvider).playAudioBytes(bytes);
        }
      } else if (type == 'error') {
        state = state.copyWith(
          isStreaming: false,
          isLoading: false,
          statusMessage: null,
          errorMessage: data.toString(),
        );
      }
    });
  }

  void sendMessage(String text) {
    final trimmed = text.trim();
    if (trimmed.isEmpty) return;

    // Interrupt previous playback
    _ref.read(audioServiceProvider).stopAudio();

    final userMsg = MessageModel(
      id: const Uuid().v4(),
      conversationId: state.conversationId,
      role: MessageRole.user,
      content: trimmed,
      timestamp: DateTime.now(),
    );

    state = state.copyWith(
      messages: [...state.messages, userMsg],
      errorMessage: null,
    );

    _ref.read(webSocketServiceProvider).sendTextMessage(trimmed);
  }

  void cancelCurrentResponse() {
    _ref.read(webSocketServiceProvider).cancelGeneration();
    _ref.read(audioServiceProvider).stopAudio();
    state = state.copyWith(isStreaming: false, statusMessage: 'Cancelled');
  }

  @override
  void dispose() {
    _wsSub?.cancel();
    super.dispose();
  }
}

final chatProvider = StateNotifierProvider.family<ChatNotifier, ChatState, String>((ref, convId) {
  return ChatNotifier(ref, convId);
});
