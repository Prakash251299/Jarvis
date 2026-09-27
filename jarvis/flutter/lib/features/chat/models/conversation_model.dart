import 'message_model.dart';

class ConversationModel {
  final String id;
  final String title;
  final DateTime createdAt;
  final DateTime updatedAt;
  final String modelUsed;
  final bool isArchived;
  final List<MessageModel> messages;
  final int messageCount;

  const ConversationModel({
    required this.id,
    required this.title,
    required this.createdAt,
    required this.updatedAt,
    required this.modelUsed,
    this.isArchived = false,
    this.messages = const [],
    this.messageCount = 0,
  });

  ConversationModel copyWith({
    String? id,
    String? title,
    DateTime? createdAt,
    DateTime? updatedAt,
    String? modelUsed,
    bool? isArchived,
    List<MessageModel>? messages,
    int? messageCount,
  }) {
    return ConversationModel(
      id: id ?? this.id,
      title: title ?? this.title,
      createdAt: createdAt ?? this.createdAt,
      updatedAt: updatedAt ?? this.updatedAt,
      modelUsed: modelUsed ?? this.modelUsed,
      isArchived: isArchived ?? this.isArchived,
      messages: messages ?? this.messages,
      messageCount: messageCount ?? this.messageCount,
    );
  }

  factory ConversationModel.fromJson(Map<String, dynamic> json) {
    return ConversationModel(
      id: json['id'] as String,
      title: json['title'] as String? ?? 'New Conversation',
      createdAt: json['created_at'] != null
          ? DateTime.tryParse(json['created_at'] as String) ?? DateTime.now()
          : DateTime.now(),
      updatedAt: json['updated_at'] != null
          ? DateTime.tryParse(json['updated_at'] as String) ?? DateTime.now()
          : DateTime.now(),
      modelUsed: json['model_used'] as String? ?? 'qwen3:8b',
      isArchived: json['is_archived'] as bool? ?? false,
      messageCount: json['message_count'] as int? ?? 0,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'title': title,
      'created_at': createdAt.toIso8601String(),
      'updated_at': updatedAt.toIso8601String(),
      'model_used': modelUsed,
      'is_archived': isArchived,
      'message_count': messageCount,
    };
  }
}
