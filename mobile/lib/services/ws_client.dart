import 'dart:async';
import 'dart:convert';

import 'package:web_socket_channel/io.dart';

import '../models.dart';

class WsClient {
  final _messages = StreamController<JsonMap>.broadcast();
  final _states = StreamController<String>.broadcast();
  Stream<JsonMap> get messages => _messages.stream;
  Stream<String> get states => _states.stream;
  IOWebSocketChannel? _channel;
  StreamSubscription<dynamic>? _subscription;
  Timer? _retry;
  PairingSession? _session;
  int _generation = 0;
  int _attempt = 0;
  bool _disposed = false;

  void connect(PairingSession session) {
    if (_disposed) return;
    stop();
    _session = session;
    _attempt = 0;
    unawaited(_open(_generation));
  }

  Future<void> _open(int generation) async {
    final session = _session;
    if (_disposed || session == null || generation != _generation) return;
    _states.add(_attempt == 0 ? 'Đang kết nối' : 'Đang nối lại');
    final uri = session.server
        .resolve('/api/v1/ws')
        .replace(scheme: session.server.scheme == 'https' ? 'wss' : 'ws');
    final channel = IOWebSocketChannel.connect(
      uri,
      headers: {'Authorization': 'Bearer ${session.deviceSecret}'},
      pingInterval: const Duration(seconds: 20),
      connectTimeout: const Duration(seconds: 10),
    );
    _channel = channel;
    // Listen immediately so failed handshakes have an error handler.
    _subscription = channel.stream.listen(
      (raw) {
        if (generation != _generation || _disposed) return;
        try {
          if (raw is! String) throw const FormatException();
          final message = jsonObject(jsonDecode(raw));
          if (message['type'] != 'pong') _messages.add(message);
        } catch (_) {
          _states.add('Bỏ qua message WS sai JSON');
        }
      },
      onError: (Object error) {
        if (generation == _generation && !_disposed) {
          _states.add('WS tạm mất kết nối');
        }
      },
      onDone: () {
        if (generation != _generation || _disposed) return;
        if (channel.closeCode == 1008) {
          _states.add('Khóa bị từ chối');
          return;
        }
        _schedule(generation);
      },
    );
    try {
      await channel.ready;
      if (generation != _generation || _disposed) {
        unawaited(channel.sink.close());
        return;
      }
      _attempt = 0;
      _states.add('Đã kết nối');
      // Backend handles textual ping; WebSocket protocol ping also checks liveness.
      channel.sink.add('ping');
    } catch (_) {
      if (generation == _generation && !_disposed) _schedule(generation);
    }
  }

  void _schedule(int generation) {
    if (_retry?.isActive == true || generation != _generation || _disposed) {
      return;
    }
    const delays = [1, 2, 4, 8, 15];
    final seconds = delays[_attempt.clamp(0, delays.length - 1)];
    _attempt++;
    _states.add('Nối lại sau $seconds giây');
    _retry = Timer(Duration(seconds: seconds), () async {
      await _subscription?.cancel();
      unawaited(_channel?.sink.close() ?? Future<void>.value());
      if (generation == _generation && !_disposed) unawaited(_open(generation));
    });
  }

  void stop() {
    _generation++;
    _session = null;
    _retry?.cancel();
    _retry = null;
    unawaited(_subscription?.cancel() ?? Future<void>.value());
    _subscription = null;
    unawaited(_channel?.sink.close() ?? Future<void>.value());
    _channel = null;
  }

  Future<void> dispose() async {
    stop();
    _disposed = true;
    await _messages.close();
    await _states.close();
  }
}
