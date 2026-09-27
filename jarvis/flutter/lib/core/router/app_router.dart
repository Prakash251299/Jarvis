import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:uuid/uuid.dart';

import '../../features/chat/screens/chat_screen.dart';
import '../../features/history/screens/history_screen.dart';
import '../../features/settings/screens/settings_screen.dart';

final appRouterProvider = Provider<GoRouter>((ref) {
  return GoRouter(
    initialLocation: '/',
    routes: [
      GoRoute(
        path: '/',
        redirect: (context, state) {
          final defaultId = const Uuid().v4();
          return '/chat/$defaultId';
        },
      ),
      GoRoute(
        path: '/chat/:id',
        builder: (context, state) {
          final convId = state.pathParameters['id'] ?? const Uuid().v4();
          return ChatScreen(conversationId: convId);
        },
      ),
      GoRoute(
        path: '/history',
        builder: (context, state) => const HistoryScreen(),
      ),
      GoRoute(
        path: '/settings',
        builder: (context, state) => const SettingsScreen(),
      ),
    ],
  );
});
