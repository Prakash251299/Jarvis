import 'dart:async';
import 'dart:io';
import 'package:flutter/foundation.dart';
import 'package:flutter_sound/flutter_sound.dart';
import 'package:just_audio/just_audio.dart';
import 'package:path_provider/path_provider.dart';
import 'package:permission_handler/permission_handler.dart';

class AudioService {
  final FlutterSoundRecorder _recorder = FlutterSoundRecorder();
  final AudioPlayer _player = AudioPlayer();

  final ValueNotifier<bool> isRecording = ValueNotifier(false);
  final ValueNotifier<bool> isPlaying = ValueNotifier(false);

  final _waveformController = StreamController<double>.broadcast();
  Stream<double> get waveformStream => _waveformController.stream;

  bool _recorderReady = false;
  String? _recordingFilePath;
  StreamSubscription? _recorderSub;

  Future<void> init() async {
    if (_recorderReady) return;
    final status = await Permission.microphone.request();
    if (status.isGranted) {
      await _recorder.openRecorder();
      await _recorder.setSubscriptionDuration(const Duration(milliseconds: 60));
      _recorderReady = true;
    }

    _player.playerStateStream.listen((state) {
      isPlaying.value = state.playing && state.processingState != ProcessingState.completed;
    });
  }

  Future<void> startRecording() async {
    await init();
    if (!_recorderReady || isRecording.value) return;

    final tempDir = await getTemporaryDirectory();
    _recordingFilePath = '${tempDir.path}/jarvis_input_${DateTime.now().millisecondsSinceEpoch}.wav';

    await _recorder.startRecorder(
      toFile: _recordingFilePath,
      codec: Codec.pcm16WAV,
      sampleRate: 16000,
      numChannels: 1,
    );

    _recorderSub = _recorder.onProgress?.listen((e) {
      final db = (e.decibels ?? 0.0).clamp(0.0, 100.0);
      _waveformController.add(db / 100.0);
    });

    isRecording.value = true;
  }

  Future<Uint8List?> stopRecording() async {
    if (!isRecording.value) return null;

    await _recorder.stopRecorder();
    await _recorderSub?.cancel();
    isRecording.value = false;

    if (_recordingFilePath != null) {
      final file = File(_recordingFilePath!);
      if (await file.exists()) {
        final bytes = await file.readAsBytes();
        await file.delete();
        _recordingFilePath = null;
        return bytes;
      }
    }
    return null;
  }

  Future<void> playAudioBytes(Uint8List audioBytes) async {
    await stopAudio();
    final tempDir = await getTemporaryDirectory();
    final tempFile = File('${tempDir.path}/jarvis_tts_${DateTime.now().millisecondsSinceEpoch}.wav');
    await tempFile.writeAsBytes(audioBytes);

    try {
      await _player.setFilePath(tempFile.path);
      await _player.play();
    } catch (e) {
      debugPrint('Audio playback error: $e');
    }
  }

  Future<void> stopAudio() async {
    if (isPlaying.value) {
      await _player.stop();
    }
  }

  void dispose() {
    _recorder.closeRecorder();
    _player.dispose();
    _recorderSub?.cancel();
    _waveformController.close();
    isRecording.dispose();
    isPlaying.dispose();
  }
}
