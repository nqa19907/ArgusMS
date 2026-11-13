import 'dart:async';
import 'dart:convert';

import 'package:firebase_messaging/firebase_messaging.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';
import 'package:mobile/app_controller.dart';
import 'package:mobile/fixtures.dart';
import 'package:mobile/models.dart';
import 'package:mobile/services/api_client.dart';
import 'package:mobile/services/device_store.dart';
import 'package:mobile/services/notification_service.dart';
import 'package:mobile/services/ws_client.dart';

final savedSession = PairingSession(
  server: Uri.parse('http://localhost:8000'),
  deviceId: 'dev-fixture',
  deviceSecret: 'fixture-not-real',
  installationId: 'installation-demo',
);

class MemoryStore extends DeviceStore {
  PairingSession? value = savedSession;
  @override
  Future<PairingSession?> loadPairing() async => value;
  @override
  Future<void> savePairing(PairingSession session) async {
    value = session;
  }

  @override
  Future<void> clearPairing() async {
    value = null;
  }
}

class FakeWs extends WsClient {
  final input = StreamController<JsonMap>.broadcast();
  final stateInput = StreamController<String>.broadcast();
  int connections = 0;
  int stops = 0;
  @override
  Stream<JsonMap> get messages => input.stream;
  @override
  Stream<String> get states => stateInput.stream;
  @override
  void connect(PairingSession session) {
    connections++;
  }

  @override
  void stop() {
    stops++;
  }

  @override
  Future<void> dispose() async {
    await input.close();
    await stateInput.close();
  }
}

class FakeNotifications extends NotificationService {
  final input = StreamController<PushMessage>.broadcast();
  @override
  Stream<PushMessage> get messages => input.stream;
  @override
  Future<void> initialize() async {
    ready = true;
  }

  @override
  Future<void> dispose() async {
    await input.close();
    await super.dispose();
  }
}

Future<void> flush() async {
  for (var i = 0; i < 8; i++) {
    await Future<void>.delayed(Duration.zero);
  }
}

void main() {
  test(
    'pause/resume does not create duplicate sockets and restores status',
    () async {
      final ws = FakeWs();
      final store = MemoryStore();
      final controller = AppController(
        ws: ws,
        store: store,
        notifications: FakeNotifications(),
        api: ApiClient(
          client: MockClient(
            (_) async => http.Response(jsonEncode(statusFixture()), 200),
          ),
        ),
      );
      await controller.initialize();
      await flush();
      expect(controller.backendOnline, true);
      expect(ws.connections, 1);
      controller.setForeground(false);
      controller.setForeground(false);
      expect(ws.stops, 1);
      controller.setForeground(true);
      controller.setForeground(true);
      await flush();
      expect(ws.connections, 2);
      controller.dispose();
      await flush();
    },
  );
  test(
    'revoked key clears secure pairing and stops realtime connection',
    () async {
      final ws = FakeWs();
      final store = MemoryStore();
      final controller = AppController(
        ws: ws,
        store: store,
        notifications: FakeNotifications(),
        api: ApiClient(
          client: MockClient((_) async => http.Response('{}', 401)),
        ),
      );
      await controller.initialize();
      await flush();
      expect(controller.pairing, isNull);
      expect(store.value, isNull);
      expect(controller.error, contains('thu hồi'));
      expect(ws.stops, greaterThan(0));
      controller.dispose();
      await flush();
    },
  );
  test(
    'same WS/FCM event is deduplicated; wrong installation is ignored',
    () async {
      final ws = FakeWs();
      final push = FakeNotifications();
      final controller = AppController(
        ws: ws,
        store: MemoryStore(),
        notifications: push,
        api: ApiClient(
          client: MockClient(
            (_) async => http.Response(jsonEncode(statusFixture()), 200),
          ),
        ),
      );
      await controller.initialize();
      await flush();
      final event = eventFixture();
      ws.input.add(event);
      await flush();
      expect(controller.eventSource, 'WebSocket');
      push.input.add(
        PushMessage(
          RemoteMessage(
            data: {...event, 'schema_version': '1', 'is_test': 'true'},
          ),
        ),
      );
      await flush();
      expect(controller.eventSource, 'WebSocket');
      ws.input.add({
        ...event,
        'event_id': 'another-event',
        'installation_id': 'wrong-backend',
      });
      await flush();
      expect(controller.lastEvent?.eventId, event['event_id']);
      controller.dispose();
      await flush();
    },
  );
}
