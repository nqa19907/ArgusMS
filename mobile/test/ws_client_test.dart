import 'dart:async';
import 'dart:convert';
import 'dart:io';

import 'package:flutter_test/flutter_test.dart';
import 'package:mobile/fixtures.dart';
import 'package:mobile/models.dart';
import 'package:mobile/services/ws_client.dart';

void main() {
  test(
    'real WS handshake uses Bearer; stop cancels pending reconnect',
    () async {
      final server = await HttpServer.bind(InternetAddress.loopbackIPv4, 0);
      var connections = 0;
      final accepted = Completer<WebSocket>();
      server.listen((request) async {
        expect(request.uri.path, '/api/v1/ws');
        expect(request.headers.value('Authorization'), 'Bearer fixture-secret');
        final socket = await WebSocketTransformer.upgrade(request);
        connections++;
        if (!accepted.isCompleted) accepted.complete(socket);
        socket.listen((message) {});
      });
      final ws = WsClient();
      final states = <String>[];
      final stateSubscription = ws.states.listen(states.add);
      final next = ws.messages.first;
      ws.connect(
        PairingSession(
          server: Uri.parse('http://127.0.0.1:${server.port}'),
          deviceId: 'dev-test',
          deviceSecret: 'fixture-secret',
          installationId: 'installation-demo',
        ),
      );
      final socket = await accepted.future.timeout(const Duration(seconds: 3));
      socket.add(jsonEncode(eventFixture()));
      expect(
        (await next.timeout(const Duration(seconds: 3)))['type'],
        'fall.confirmed',
      );
      await socket.close();
      await Future<void>.delayed(const Duration(milliseconds: 100));
      expect(states.any((state) => state.startsWith('Nối lại')), true);
      ws.stop();
      await Future<void>.delayed(const Duration(milliseconds: 1200));
      expect(connections, 1);
      await stateSubscription.cancel();
      await ws.dispose();
      await server.close(force: true);
    },
  );
}
