import 'dart:async';
import 'dart:collection';

import 'package:flutter/foundation.dart';

import 'config.dart';
import 'fixtures.dart';
import 'models.dart';
import 'services/api_client.dart';
import 'services/device_store.dart';
import 'services/notification_service.dart';
import 'services/ws_client.dart';

class AppController extends ChangeNotifier {
  AppController({
    ApiClient? api,
    DeviceStore? store,
    WsClient? ws,
    NotificationService? notifications,
  }) : api = api ?? ApiClient(),
       store = store ?? DeviceStore(),
       ws = ws ?? WsClient(),
       notifications = notifications ?? NotificationService();

  final ApiClient api;
  final DeviceStore store;
  final WsClient ws;
  final NotificationService notifications;
  final List<StreamSubscription<dynamic>> _subscriptions = [];
  final LinkedHashSet<String> _seen = LinkedHashSet();
  PairingSession? pairing;
  SystemStatus? status;
  FallEvent? lastEvent;
  String eventSource = '';
  String? error;
  String? notice;
  String? pushError;
  int foregroundPushCount = 0;
  int openedPushCount = 0;
  String wsState = 'Chưa kết nối';
  bool loading = true;
  bool busy = false;
  bool isDemo = false;
  bool backendOnline = false;
  bool pushSynced = false;
  bool _foreground = true;
  bool _disposed = false;
  bool _refreshing = false;
  bool _registering = false;
  int _generation = 0;
  Timer? _poll;
  DateTime? statusReceivedAt;
  bool get hasSession => pairing != null || isDemo;
  bool get registeringPush => _registering;

  void _changed() {
    if (!_disposed) notifyListeners();
  }

  Future<void> initialize() async {
    _subscriptions.add(ws.messages.listen(_onWs));
    _subscriptions.add(
      ws.states.listen((state) {
        wsState = state;
        if (state == 'Khóa bị từ chối') unawaited(refresh());
        _changed();
      }),
    );
    _subscriptions.add(notifications.notices.listen((_) => _changed()));
    _subscriptions.add(
      notifications.tokens.listen((token) {
        if (pairing != null) unawaited(_registerToken(token));
      }),
    );
    _subscriptions.add(
      notifications.messages.listen((push) {
        try {
          final event = FallEvent.fromPushData(push.message.data);
          if (event.installationId != pairing?.installationId) return;
          if (push.opened) {
            openedPushCount++;
          } else if (_foreground) {
            foregroundPushCount++;
          }
          _receive(
            event,
            push.opened ? 'Chạm thông báo FCM' : 'FCM foreground',
            opened: push.opened,
          );
          _changed();
        } on FormatException {
          error = 'Bỏ qua push sai schema; kiểm tra payload với SV2.';
          _changed();
        }
      }),
    );
    try {
      pairing = await store.loadPairing();
    } catch (_) {
      error = 'Không đọc được thông tin ghép. Có thể xóa dữ liệu ghép cũ rồi thử lại.';
    }
    loading = false;
    _changed();
    if (pairing != null) _startConnection();
    // Firebase failures never block the UI, pairing, status or WS.
    unawaited(
      notifications.initialize().then((_) {
        _changed();
        if (pairing != null && notifications.allowed) unawaited(registerPush());
      }),
    );
  }

  String _friendly(Object exception) => switch (exception) {
    ApiException e => e.message,
    FormatException e => e.message,
    StateError e => e.message,
    TimeoutException _ =>
      'FCM phản hồi quá chậm. Kiểm tra Internet và Google Play.',
    _ => 'Thao tác thất bại. Kiểm tra kết nối/cấu hình rồi thử lại.',
  };

  Future<void> _handleError(Object exception) async {
    if (exception is ApiException && exception.unauthorized) {
      await _clearLocal();
    }
    error = _friendly(exception);
    _changed();
  }

  Future<void> checkHealth(String linkText) async {
    if (busy) return;
    busy = true;
    error = null;
    notice = null;
    _changed();
    try {
      await api.health(PairingLink.parse(linkText).server);
      notice =
          'API đang sống. Health chưa xác nhận camera, AI hoặc push sẵn sàng.';
    } catch (e) {
      error = _friendly(e);
    } finally {
      busy = false;
      _changed();
    }
  }

  Future<void> pair(String linkText) async {
    if (busy) return;
    busy = true;
    error = null;
    notice = null;
    _changed();
    try {
      final session = await api.pair(PairingLink.parse(linkText));
      try {
        await store.savePairing(session);
      } catch (_) {
        throw StateError(
          'Claim thành công nhưng không lưu được khóa. Kiểm tra secure storage và tạo link mới.',
        );
      }
      pairing = session;
      isDemo = false;
      _generation++;
      _seen.clear();
      notice = 'Đã ghép thiết bị. Đang lấy trạng thái backend.';
      _startConnection();
    } catch (e) {
      error = _friendly(e);
    } finally {
      busy = false;
      _changed();
    }
  }

  void _startConnection() {
    final session = pairing;
    if (session == null || !_foreground || _disposed) return;
    ws.connect(session);
    _poll?.cancel();
    _poll = Timer.periodic(
      AppConfig.statusInterval,
      (_) => unawaited(refresh()),
    );
    unawaited(refresh());
  }

  Future<void> refresh() async {
    final session = pairing;
    if (session == null || _refreshing || !_foreground || _disposed) return;
    final generation = _generation;
    _refreshing = true;
    try {
      final current = await api.getStatus(session);
      if (generation != _generation || _disposed) return;
      status = current;
      backendOnline = true;
      statusReceivedAt = DateTime.now();
      error = null;
    } catch (e) {
      if (generation != _generation || _disposed) return;
      backendOnline = false;
      await _handleError(e);
    } finally {
      _refreshing = false;
      _changed();
    }
  }

  void _onWs(JsonMap message) {
    if (!_foreground || pairing == null) return;
    try {
      switch (message['type']) {
        case 'fall.confirmed':
          _receive(FallEvent.fromJson(message), 'WebSocket');
        case 'camera.status':
        case 'ai.status':
          unawaited(refresh());
        default:
          break;
      }
    } on FormatException {
      error = 'Bỏ qua sự kiện WS sai schema; cần đối chiếu contract SV2.';
      _changed();
    }
  }

  void _receive(FallEvent event, String source, {bool opened = false}) {
    final installation = isDemo ? 'installation-demo' : pairing?.installationId;
    if (installation == null || event.installationId != installation) return;
    if (!_foreground && !opened) return;
    final key = '${event.installationId}/${event.eventId}';
    if (_seen.contains(key) && !opened) return;
    _seen.add(key);
    if (_seen.length > 100) _seen.remove(_seen.first);
    lastEvent = event;
    eventSource = source;
    _changed();
  }

  Future<void> registerPush() async {
    if (_registering || pairing == null || isDemo || _disposed) return;
    _registering = true;
    pushError = null;
    _changed();
    try {
      final generation = _generation;
      final token = await notifications.requestEndpoint();
      if (generation != _generation || _disposed) return;
      await _registerToken(token);
    } catch (e) {
      pushError = _friendly(e);
      error = pushError;
    } finally {
      _registering = false;
      _changed();
    }
  }

  Future<void> _registerToken(String token) async {
    final session = pairing;
    if (session == null || _disposed) return;
    final generation = _generation;
    pushSynced = false;
    try {
      await api.registerPush(session, token);
      if (generation != _generation || _disposed) return;
      pushSynced = true;
      pushError = null;
      notice =
          'Backend đã lưu endpoint. Cần nhận push thử để xác nhận đường FCM.';
      error = null;
    } catch (e) {
      if (generation == _generation && !_disposed) {
        pushError = _friendly(e);
        await _handleError(e);
      }
    }
    _changed();
  }

  Future<void> sendTest() async {
    final session = pairing;
    if (session == null || busy || !pushSynced) return;
    final generation = _generation;
    busy = true;
    error = null;
    _changed();
    try {
      final eventId = await api.sendTest(session);
      if (generation != _generation || _disposed) return;
      notice =
          'Backend nhận yêu cầu thử: $eventId. HTTP 202/WS không chứng minh FCM đã đến.';
    } catch (e) {
      if (generation == _generation && !_disposed) await _handleError(e);
    } finally {
      busy = false;
      _changed();
    }
  }

  Future<void> unpair({bool localOnly = false}) async {
    if (busy) return;
    busy = true;
    error = null;
    _changed();
    try {
      if (!localOnly && pairing != null) await api.revoke(pairing!);
      await _clearLocal();
      notice = localOnly
          ? 'Đã quên khóa trên app. Thiết bị có thể còn active tại backend; nhờ SV2 revoke.'
          : 'Đã thu hồi thiết bị và xóa thông tin ghép.';
    } catch (e) {
      if (e is ApiException && e.unauthorized) {
        await _clearLocal();
      } else {
        error = 'Chưa hủy ghép được. Có thể Quên trên app nếu offline; cần revoke phía server sau.';
      }
    } finally {
      busy = false;
      _changed();
    }
  }

  Future<void> _clearLocal() async {
    _generation++;
    _poll?.cancel();
    ws.stop();
    pairing = null;
    isDemo = false;
    status = null;
    lastEvent = null;
    _seen.clear();
    pushSynced = false;
    pushError = null;
    foregroundPushCount = 0;
    openedPushCount = 0;
    backendOnline = false;
    statusReceivedAt = null;
    wsState = 'Chưa kết nối';
    await store.clearPairing();
  }

  void setForeground(bool active) {
    if (_foreground == active || _disposed) return;
    _foreground = active;
    if (active) {
      _startConnection();
      final token = notifications.cachedEndpoint;
      if (token != null && !pushSynced) unawaited(_registerToken(token));
    } else {
      _poll?.cancel();
      ws.stop();
      wsState = 'Tạm dừng khi app ở nền';
    }
    _changed();
  }

  void useDemo() {
    if (busy || pairing != null) return;
    isDemo = true;
    error = null;
    notice = null;
    status = SystemStatus.fromJson(statusFixture());
    _changed();
  }

  void cycleDemo() {
    if (!isDemo) return;
    final connected = status?.cameraState != 'CONNECTED';
    status = SystemStatus.fromJson(
      statusFixture(
        camera: connected ? 'CONNECTED' : 'RECONNECTING',
        ai: connected ? 'ERROR' : 'WARMUP',
      ),
    );
    _changed();
  }

  void demoEvent() {
    if (isDemo) _receive(FallEvent.fromJson(eventFixture()), 'Fixture demo');
  }

  void dismissEvent() {
    lastEvent = null;
    _changed();
  }

  @override
  void dispose() {
    _disposed = true;
    _generation++;
    _poll?.cancel();
    for (final subscription in _subscriptions) {
      unawaited(subscription.cancel());
    }
    unawaited(ws.dispose());
    unawaited(notifications.dispose());
    api.close();
    super.dispose();
  }
}
