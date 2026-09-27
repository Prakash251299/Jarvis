enum MessageRole {
  user,
  assistant,
  system;

  static MessageRole fromString(String role) {
    switch (role.toLowerCase()) {
      case 'assistant':
        return MessageRole.assistant;
      case 'system':
        return MessageRole.system;
      case 'user':
      default:
        return MessageRole.user;
    }
  }

  String toApiString() {
    return name;
  }
}

class MessageModel {
  final String id;
  final String conversationId;
  final MessageRole role;
  final String content;
  final DateTime timestamp;
  final bool isStreaming;
  final bool hasAudio;
  final String? audioPath;
  final int? tokensUsed;

  const MessageModel({
    required this.id,
    required this.conversationId,
    required this.role,
    required this.content,
    required this.timestamp,
    this.isStreaming = false,
    this.hasAudio = false,
    this.audioPath,
    this.tokensUsed,
  });

  bool get isUser => role == MessageRole.user;
  bool get isAssistant => role == MessageRole.assistant;
  bool get isSystem => role == MessageRole.system;

  MessageModel copyWith({
    String? id,
    String? conversationId,
    MessageRole? role,
    String? content,
    DateTime? timestamp,
    bool? isStreaming,
    bool? hasAudio,
    String? audioPath,
    int? tokensUsed,
  }) {
    return MessageModel(
      id: id ?? this.id,
      conversationId: conversationId ?? this.conversationId,
      role: role ?? this.role,
      content: content ?? this.content,
      timestamp: timestamp ?? this.timestamp,
      isStreaming: isStreaming ?? this.isStreaming,
      hasAudio: hasAudio ?? this.hasAudio,
      audioPath: audioPath ?? this.audioPath,
      tokensUsed: tokensUsed ?? this.tokensUsed,
    );
  }

  factory MessageModel.fromJson(Map<String, dynamic> json) {
    return MessageModel(
      id: json['id'] as String,
      conversationId: json['conversation_id'] as String? ?? '',
      role: MessageRole.fromString(json['role'] as String? ?? 'user'),
      content: json['content'] as String? ?? '',
      timestamp: json['timestamp'] != null
          ? DateTime.tryParse(json['timestamp'] as String) ?? DateTime.now()
          : DateTime.now(),
      isStreaming: json['is_streaming'] as bool? ?? false,
      hasAudio: json['has_audio'] as bool? ?? false,
      audioPath: json['audio_path'] as String?,
      tokensUsed: json['tokens_used'] as int?,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'conversation_id': conversationId,
      'role': role.toApiString(),
      'content': content,
      'timestamp': timestamp.toIso8601String(),
      'tokens_used': tokensUsed,
      'audio_path': audioPath,
    };
  }
}
