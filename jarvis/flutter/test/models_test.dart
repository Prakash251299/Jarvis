import 'package:flutter_test/flutter_test.dart';
import 'package:jarvis/features/chat/models/message_model.dart';
import 'package:jarvis/features/chat/models/conversation_model.dart';
import 'package:jarvis/features/settings/models/settings_model.dart';

void main() {
  group('MessageModel Tests', () {
    test('serialization and deserialization', () {
      final now = DateTime.now();
      final msg = MessageModel(
        id: 'msg-1',
        conversationId: 'conv-1',
        role: MessageRole.user,
        content: 'Hello Jarvis',
        timestamp: now,
        tokensUsed: 15,
      );

      expect(msg.isUser, isTrue);
      expect(msg.isAssistant, isFalse);

      final json = msg.toJson();
      expect(json['id'], 'msg-1');
      expect(json['role'], 'user');
      expect(json['content'], 'Hello Jarvis');

      final deserialized = MessageModel.fromJson(json);
      expect(deserialized.id, msg.id);
      expect(deserialized.role, MessageRole.user);
      expect(deserialized.content, msg.content);
    });

    test('copyWith works correctly', () {
      final msg = MessageModel(
        id: 'msg-1',
        conversationId: 'conv-1',
        role: MessageRole.assistant,
        content: 'Generating...',
        timestamp: DateTime.now(),
        isStreaming: true,
      );

      final updated = msg.copyWith(content: 'Done!', isStreaming: false);
      expect(updated.id, 'msg-1');
      expect(updated.content, 'Done!');
      expect(updated.isStreaming, false);
      expect(updated.role, MessageRole.assistant);
    });
  });

  group('ConversationModel Tests', () {
    test('serialization and deserialization', () {
      final conv = ConversationModel(
        id: 'conv-123',
        title: 'Project Discussion',
        createdAt: DateTime.now(),
        updatedAt: DateTime.now(),
        modelUsed: 'qwen3:8b',
        messageCount: 5,
      );

      final json = conv.toJson();
      expect(json['id'], 'conv-123');
      expect(json['title'], 'Project Discussion');

      final deserialized = ConversationModel.fromJson(json);
      expect(deserialized.id, 'conv-123');
      expect(deserialized.title, 'Project Discussion');
      expect(deserialized.messageCount, 5);
    });
  });

  group('SettingsModel Tests', () {
    test('default settings and json roundtrip', () {
      const defaults = SettingsModel();
      expect(defaults.model, 'qwen3:8b');
      expect(defaults.whisperModel, 'base');
      expect(defaults.voiceOutputEnabled, isTrue);

      final json = defaults.toJson();
      final fromJson = SettingsModel.fromJson(json);
      expect(fromJson.model, defaults.model);
      expect(fromJson.whisperModel, defaults.whisperModel);
      expect(fromJson.piperVoice, defaults.piperVoice);
    });
  });
}
