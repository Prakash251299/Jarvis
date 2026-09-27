import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../providers/settings_provider.dart';

class SettingsScreen extends ConsumerWidget {
  const SettingsScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final settings = ref.watch(settingsProvider);
    final availableModelsAsync = ref.watch(availableModelsProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Settings'),
      ),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          const Text('Local LLM (Ollama)', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16)),
          const SizedBox(height: 8),
          availableModelsAsync.when(
            loading: () => const LinearProgressIndicator(),
            error: (_, __) => Text('Current Model: ${settings.model}'),
            data: (models) {
              final items = models.contains(settings.model) ? models : [...models, settings.model];
              return DropdownButtonFormField<String>(
                initialValue: settings.model,
                decoration: const InputDecoration(labelText: 'Ollama Model'),
                items: items.map((m) => DropdownMenuItem(value: m, child: Text(m))).toList(),
                onChanged: (val) {
                  if (val != null) ref.read(settingsProvider.notifier).updateModel(val);
                },
              );
            },
          ),
          const SizedBox(height: 24),
          const Text('Voice & Audio', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16)),
          SwitchListTile(
            title: const Text('Voice Output (TTS)'),
            subtitle: const Text('Automatically speak assistant responses using Piper'),
            value: settings.voiceOutputEnabled,
            onChanged: (val) => ref.read(settingsProvider.notifier).toggleVoice(val),
          ),
          DropdownButtonFormField<String>(
            initialValue: settings.whisperModel,
            decoration: const InputDecoration(labelText: 'Whisper Model (STT)'),
            items: const [
              DropdownMenuItem(value: 'tiny', child: Text('tiny (Fastest)')),
              DropdownMenuItem(value: 'base', child: Text('base (Recommended)')),
              DropdownMenuItem(value: 'small', child: Text('small')),
              DropdownMenuItem(value: 'medium', child: Text('medium (Higher accuracy)')),
            ],
            onChanged: (val) {
              if (val != null) ref.read(settingsProvider.notifier).updateWhisperModel(val);
            },
          ),
          const SizedBox(height: 16),
          TextFormField(
            initialValue: settings.piperVoice,
            decoration: const InputDecoration(
              labelText: 'Piper Voice Model Name',
              hintText: 'e.g. en_US-lessac-medium',
            ),
            onFieldSubmitted: (val) {
              if (val.trim().isNotEmpty) ref.read(settingsProvider.notifier).updatePiperVoice(val.trim());
            },
          ),
          const SizedBox(height: 24),
          const Text('Memory & Context', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16)),
          SwitchListTile(
            title: const Text('Persistent Memory'),
            subtitle: const Text('Retain personal user context and facts across sessions'),
            value: settings.memoryEnabled,
            onChanged: (val) => ref.read(settingsProvider.notifier).toggleMemory(val),
          ),
          const SizedBox(height: 32),
          const Center(
            child: Text(
              'Jarvis v1.0.0 • Completely Private & Local',
              style: TextStyle(color: Colors.grey, fontSize: 12),
            ),
          ),
        ],
      ),
    );
  }
}
