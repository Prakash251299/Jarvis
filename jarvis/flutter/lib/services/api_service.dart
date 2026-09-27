import 'package:dio/dio.dart';
import 'package:flutter/foundation.dart';
import '../core/constants/app_constants.dart';
import '../features/chat/models/conversation_model.dart';
import '../features/chat/models/message_model.dart';
import '../features/settings/models/settings_model.dart';

class ApiService {
  final Dio _dio;

  ApiService({Dio? dio})
      : _dio = dio ??
            Dio(
              BaseOptions(
                baseUrl: '${AppConstants.backendBaseUrl}${AppConstants.apiVersion}',
                connectTimeout: const Duration(seconds: 10),
                receiveTimeout: const Duration(seconds: 60),
                headers: {'Content-Type': 'application/json'},
              ),
            );

  Future<ConversationModel> createConversation({String? title, String? model}) async {
    final response = await _dio.post(
      '/conversations',
      data: {'title': title ?? 'New Conversation', 'model': model},
    );
    return ConversationModel.fromJson(response.data as Map<String, dynamic>);
  }

  Future<List<ConversationModel>> listConversations() async {
    final response = await _dio.get('/conversations');
    final data = response.data as Map<String, dynamic>;
    final list = data['conversations'] as List<dynamic>? ?? [];
    return list.map((e) => ConversationModel.fromJson(e as Map<String, dynamic>)).toList();
  }

  Future<List<MessageModel>> getMessages(String conversationId) async {
    final response = await _dio.get('/conversations/$conversationId/messages');
    final list = response.data as List<dynamic>? ?? [];
    return list.map((e) => MessageModel.fromJson(e as Map<String, dynamic>)).toList();
  }

  Future<void> deleteConversation(String conversationId) async {
    await _dio.delete('/conversations/$conversationId');
  }

  Future<List<String>> getAvailableModels() async {
    try {
      final response = await _dio.get('/llm/models');
      final list = response.data as List<dynamic>? ?? [];
      return list.map((e) => e.toString()).toList();
    } catch (e) {
      debugPrint('Failed to load Ollama models: $e');
      return [AppConstants.defaultModel];
    }
  }

  Future<SettingsModel> getSettings() async {
    final response = await _dio.get('/settings');
    return SettingsModel.fromJson(response.data as Map<String, dynamic>);
  }

  Future<SettingsModel> updateSettings(SettingsModel settings) async {
    final response = await _dio.put('/settings', data: settings.toJson());
    return SettingsModel.fromJson(response.data as Map<String, dynamic>);
  }

  Future<String> transcribeAudio(Uint8List audioBytes) async {
    final formData = FormData.fromMap({
      'file': MultipartFile.fromBytes(audioBytes, filename: 'recording.wav'),
    });
    final response = await _dio.post('/stt/transcribe', data: formData);
    final data = response.data as Map<String, dynamic>;
    return data['text'] as String? ?? '';
  }

  Future<Uint8List> synthesizeSpeech(String text, {String? voice}) async {
    final response = await _dio.post(
      '/tts/synthesize',
      data: {'text': text, 'voice': voice},
      options: Options(responseType: ResponseType.bytes),
    );
    return Uint8List.fromList(response.data as List<int>);
  }
}
