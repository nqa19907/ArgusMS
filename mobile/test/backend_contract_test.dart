import 'dart:convert';

import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:mobile/config.dart';
import 'package:mobile/models.dart';
import 'package:mobile/services/api_client.dart';
import 'package:mobile/services/ws_client.dart';

// Opt-in only; run against contract_server.py in the validation workspace.
// The server imports unmodified SV2 routes/auth/storage and substitutes camera/FCM.
const enabled = bool.fromEnvironment('ARGUS_CONTRACT_TEST');
void main() {
  test('real SV2: health → claim → status → WS → push registration → test event → revoke', () async {
    final raw = await http.get(
      Uri.parse('http://127.0.0.1:18761/__test__/pair-link'),
    );
    final link = PairingLink.parse(
      (jsonDecode(raw.body) as Map)['link'] as String,
    );
    final api = ApiClient();
    final ws = WsClient();
    try {
      await api.health(link.server);
      final session = await api.pair(link);
      expect((await api.getStatus(session)).aiMode, 'mock');
      await expectLater(
        api.pair(link),
        throwsA(
          isA<ApiException>().having(
            (e) => e.statusCode,
            'already consumed',
            409,
          ),
        ),
      );
      final connected = ws.states.firstWhere((s) => s == 'Đã kết nối');
      ws.connect(session);
      await connected.timeout(const Duration(seconds: 5));
      final received = ws.messages.firstWhere(
        (message) => message['type'] == 'fall.confirmed',
      );
      await api.registerPush(session, 'fixture-token-never-sent');
      final eventId = await api.sendTest(session);
      final event = FallEvent.fromJson(
        await received.timeout(const Duration(seconds: 5)),
      );
      expect(event.eventId, eventId);
      expect(event.installationId, session.installationId);
      expect(event.isTest, true);
      await api.revoke(session);
      await expectLater(
        api.getStatus(session),
        throwsA(
          isA<ApiException>().having((e) => e.statusCode, 'revoked', 401),
        ),
      );
    } finally {
      await ws.dispose();
      api.close();
    }
  }, skip: !enabled);
}
