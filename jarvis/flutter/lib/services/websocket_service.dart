import 'dart:async';
import 'dart:convert';
import 'package:flutter/foundation.dart';
import 'package:web_socket_channel/web_socket_channel.dart';
import '../core/constants/app_constants.dart';

enum WsConnectionState { disconnected, connecting, connected, error }

class WebSocketService {
  WebSocketChannel? _channel;
  StreamSubscription? _subscription;
  Timer? _heartbeatTimer;
  Timer? _reconnectTimer;
  String? _currentConversationId;
  int _reconnectAttempts = 0;

  final _stateController = StreamController<WsConnectionState>.broadcast();
  final _eventController = StreamController<Map<String, dynamic>>.broadcast();

  Stream<WsConnectionState> get stateStream => _stateController.stream;
  Stream<Map<String, dynamic>> get eventStream => _eventController.stream;

  WsConnectionState _currentState = WsConnectionState.disconnected;
  WsConnectionState get currentState => _currentState;

  void _setState(WsConnectionState state) {
    _currentState = state;
    if (!_stateController.isClosed) {
      _stateController.add(state);
    }
  }

  Future<void> connect(String conversationId) async {
    if (_currentState == WsConnectionState.connected && _currentConversationId == conversationId) {
      return;
    }
    disconnect();
    _currentConversationId = conversationId;
    _setState(WsConnectionState.connecting);

    final wsUri = Uri.parse('${AppConstants.wsBaseUrl}/ws/$conversationId');
    try {
      _channel = WebSocketChannel.connect(wsUri);
      await _channel!.ready;
      _setState(WsConnectionState.connected);
      _reconnectAttempts = 0;

      _subscription = _channel!.stream.listen(
        (data) {
          if (data is String) {
            try {
              final jsonMap = jsonDecode(data) as Map<String, dynamic>;
              if (jsonMap['event'] != 'pong') {
                _eventController.add(jsonMap);
              }
            } catch (e) {
              debugPrint('Failed to parse WebSocket JSON: $e');
            }
          }
        },
        onError: (err) {
          debugPrint('WebSocket error: $err');
          _setState(WsConnectionState.error);
          _scheduleReconnect();
        },
        onDone: () {
          debugPrint('WebSocket closed');
          _setState(WsConnectionState.disconnected);
          _scheduleReconnect();
        },
      );

      _startHeartbeat();
    } catch (e) {
      debugPrint('WebSocket connection exception: $e');
      _setState(WsConnectionState.error);
      _scheduleReconnect();
    }
  }

  void _startHeartbeat() {
    _heartbeatTimer?.cancel();
    _heartbeatTimer = Timer.periodic(const Duration(seconds: 25), (timer) {
      if (_currentState == WsConnectionState.connected) {
        sendJson({'event': 'ping'});
      }
    });
  }

  void _scheduleReconnect() {
    if (_reconnectAttempts >= AppConstants.wsMaxReconnectAttempts) return;
    _reconnectTimer?.cancel();
    _reconnectTimer = Timer(AppConstants.wsReconnectDelay, () {
      if (_currentConversationId != null && _currentState != WsConnectionState.connected) {
        _reconnectAttempts++;
        connect(_currentConversationId!);
      }
    });
  }

  void sendJson(Map<String, dynamic> data) {
    if (_channel != null && _currentState == WsConnectionState.connected) {
      _channel!.sink.add(jsonEncode(data));
    }
  }

  void sendTextMessage(String text) {
    sendJson({'event': 'text_message', 'data': text});
  }

  void sendAudioChunk(Uint8List bytes) {
    if (_channel != null && _currentState == WsConnectionState.connected) {
      _channel!.sink.add(bytes);
    }
  }

  void sendAudioEnd() {
    sendJson({'event': 'audio_end'});
  }

  void cancelGeneration() {
    sendJson({'event': 'cancel_generation'});
  }

  void disconnect() {
    _heartbeatTimer?.cancel();
    _reconnectTimer?.cancel();
    _subscription?.cancel();
    _channel?.sink.close();
    _channel = null;
    _setState(WsConnectionState.disconnected);
  }

  void dispose() {
    disconnect();
    _stateController.close();
    _eventController.close();
  }
}
