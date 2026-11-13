import 'dart:async';

import 'package:firebase_core/firebase_core.dart';
import 'package:firebase_messaging/firebase_messaging.dart';
import 'package:flutter_local_notifications/flutter_local_notifications.dart';

import '../firebase_options.dart';

class PushMessage {
  const PushMessage(this.message, {this.opened = false});
  final RemoteMessage message;
  final bool opened;
}

class NotificationService {
  final _messages = StreamController<PushMessage>.broadcast();
  final _tokens = StreamController<String>.broadcast();
  final _notices = StreamController<String>.broadcast();
  Stream<PushMessage> get messages => _messages.stream;
  Stream<String> get tokens => _tokens.stream;
  Stream<String> get notices => _notices.stream;
  final List<StreamSubscription<dynamic>> _subscriptions = [];
  final _plugin = FlutterLocalNotificationsPlugin();
  FirebaseMessaging? _messaging;
  bool ready = false;
  bool allowed = false;
  String state = 'Chưa khởi tạo';
  String? _token;
  bool _disposed = false;

  void _notice(String message) {
    state = message;
    if (!_disposed) _notices.add(message);
  }

  Future<void> initialize() async {
    try {
      await Firebase.initializeApp(
        options: DefaultFirebaseOptions.currentPlatform,
      ).timeout(const Duration(seconds: 12));
      if (_disposed) return;
      await createChannels();
      if (_disposed) return;
      final messaging = FirebaseMessaging.instance;
      _messaging = messaging;
      _subscriptions.add(
        FirebaseMessaging.onMessage.listen((message) {
          if (!_disposed) _messages.add(PushMessage(message));
        }),
      );
      _subscriptions.add(
        FirebaseMessaging.onMessageOpenedApp.listen((message) {
          if (!_disposed) _messages.add(PushMessage(message, opened: true));
        }),
      );
      // SV2 uses messaging.Message(token=...), so this week-1 adapter uses
      // registration tokens. Do not pass a Firebase Installation ID as token.
      _subscriptions.add(
        // ignore: deprecated_member_use
        messaging.onTokenRefresh.listen(
          (token) {
            _token = token;
            if (!_disposed) _tokens.add(token);
          },
          onError: (Object error) {
            _notice('Không làm mới được endpoint FCM. Bấm đăng ký lại.');
          },
        ),
      );
      final settings = await messaging.getNotificationSettings().timeout(
        const Duration(seconds: 5),
      );
      allowed =
          settings.authorizationStatus == AuthorizationStatus.authorized ||
          settings.authorizationStatus == AuthorizationStatus.provisional;
      ready = true;
      _notice(
        allowed
            ? 'Firebase sẵn sàng; cần đăng ký endpoint với backend.'
            : 'Firebase sẵn sàng; chưa có quyền hiển thị thông báo.',
      );
      final initial = await messaging.getInitialMessage().timeout(
        const Duration(seconds: 5),
      );
      if (initial != null && !_disposed) {
        _messages.add(PushMessage(initial, opened: true));
      }
    } catch (_) {
      _notice('Firebase/Google Play chưa sẵn sàng. HTTP và WS vẫn dùng được.');
    }
  }

  Future<void> createChannels() async {
    final android = _plugin
        .resolvePlatformSpecificImplementation<
          AndroidFlutterLocalNotificationsPlugin
        >();
    for (final channel in const [
      AndroidNotificationChannel(
        'fall_test_v0',
        'Thông báo thử',
        description: 'Smoke test tuần 1',
        importance: Importance.high,
      ),
      // Existing SV2 IDs: default sound only in week 1. Custom sound in week 3
      // requires NEW versioned IDs in BOTH Android client and backend sender.
      AndroidNotificationChannel(
        'fall_alerts_v1',
        'Cảnh báo (âm mặc định)',
        importance: Importance.high,
      ),
      AndroidNotificationChannel(
        'fall_silent_v1',
        'Cảnh báo im lặng',
        importance: Importance.high,
        playSound: false,
        enableVibration: false,
      ),
    ]) {
      await android?.createNotificationChannel(channel);
    }
  }

  Future<String> requestEndpoint() async {
    final messaging = _messaging;
    if (!ready || messaging == null) {
      throw StateError(
        'Firebase chưa sẵn sàng. Kiểm tra cấu hình, mạng và Google Play.',
      );
    }
    final settings = await messaging.requestPermission(
      alert: true,
      badge: true,
      sound: true,
    );
    allowed =
        settings.authorizationStatus == AuthorizationStatus.authorized ||
        settings.authorizationStatus == AuthorizationStatus.provisional;
    if (!allowed) {
      _notice(
        'Quyền thông báo bị từ chối. Có thể bật trong Android Settings → Apps → ArgusMS.',
      );
      throw StateError('Chưa có quyền hiển thị thông báo.');
    }
    // ignore: deprecated_member_use
    final token = await messaging.getToken().timeout(
      const Duration(seconds: 15),
    );
    if (token == null || token.isEmpty) throw StateError('FCM chưa cấp token.');
    _token = token;
    _notice('Đã có endpoint; đang đồng bộ backend.');
    return token;
  }

  String? get cachedEndpoint => _token;

  Future<void> dispose() async {
    _disposed = true;
    for (final subscription in _subscriptions) {
      await subscription.cancel();
    }
    await _messages.close();
    await _tokens.close();
    await _notices.close();
  }
}
