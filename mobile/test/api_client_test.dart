import 'dart:async';
import 'dart:convert';

import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';
import 'package:mobile/config.dart';
import 'package:mobile/fixtures.dart';
import 'package:mobile/models.dart';
import 'package:mobile/services/api_client.dart';

final session = PairingSession(
  server: nullUri,
  deviceId: 'dev-fixture',
  deviceSecret: 'fixture-secret-not-real',
  installationId: 'installation-demo',
);
// Test-only URI and credentials.
final nullUri = Uri.parse('http://localhost:8000');

void main() {
  test('claim matches SV2 request and saves returned installation', () async {
    final api = ApiClient(
      client: MockClient((request) async {
        expect(request.url.path, '/api/v1/pairing/claim');
        expect(request.method, 'POST');
        expect(request.headers.containsKey('authorization'), false);
        final body = jsonDecode(request.body) as Map;
        expect(body['pairing_code'], 'fixture-code-123');
        expect(body['expected_installation_id'], 'installation-demo');
        return http.Response(
          jsonEncode({
            'schema_version': 1,
            'device_id': 'dev-fixture',
            'device_secret': 'fixture-secret',
            'installation_id': 'installation-demo',
          }),
          201,
        );
      }),
    );
    final result = await api.pair(
      PairingLink(nullUri, 'fixture-code-123', 'installation-demo'),
    );
    expect(result.deviceId, 'dev-fixture');
    api.close();
  });
  test('status uses Bearer and validates installation', () async {
    final api = ApiClient(
      client: MockClient((request) async {
        expect(
          request.headers['Authorization'],
          'Bearer fixture-secret-not-real',
        );
        return http.Response(jsonEncode(statusFixture()), 200);
      }),
    );
    expect((await api.getStatus(session)).cameraState, 'STOPPED');
    api.close();
  });
  test('mismatched installation invalidates session', () async {
    final api = ApiClient(
      client: MockClient(
        (_) async => http.Response(
          jsonEncode({
            ...statusFixture(),
            'installation_id': 'another-backend',
          }),
          200,
        ),
      ),
    );
    await expectLater(
      api.getStatus(session),
      throwsA(
        isA<ApiException>().having((e) => e.unauthorized, 'unauthorized', true),
      ),
    );
    api.close();
  });
  test('push uses push_kind/push_value (not a nested endpoint)', () async {
    final api = ApiClient(
      client: MockClient((request) async {
        expect(request.url.path, '/api/v1/devices/dev-fixture/push');
        expect(jsonDecode(request.body), {
          'push_kind': 'fcm',
          'push_value': 'fake-token',
          'sound_enabled': true,
        });
        return http.Response(
          jsonEncode({
            'schema_version': 1,
            'device_id': 'dev-fixture',
            'updated': true,
          }),
          200,
        );
      }),
    );
    await api.registerPush(session, 'fake-token');
    api.close();
  });
  for (final code in [401, 409, 410, 422]) {
    test('HTTP $code gives a typed safe error', () async {
      final api = ApiClient(
        client: MockClient(
          (_) async => http.Response('{"detail":"secret must not leak"}', code),
        ),
      );
      await expectLater(
        api.getStatus(session),
        throwsA(
          isA<ApiException>()
              .having((e) => e.statusCode, 'code', code)
              .having(
                (e) => e.message.contains('secret must not leak'),
                'safe',
                false,
              ),
        ),
      );
      api.close();
    });
  }
  test('claim timeout is not retried and asks for a new link', () async {
    var calls = 0;
    final api = ApiClient(
      timeout: const Duration(milliseconds: 10),
      client: MockClient((_) {
        calls++;
        return Completer<http.Response>().future;
      }),
    );
    await expectLater(
      api.pair(PairingLink(nullUri, 'fixture-code-123', 'installation-demo')),
      throwsA(
        isA<ApiException>().having(
          (e) => e.message,
          'message',
          contains('Tạo link mới'),
        ),
      ),
    );
    expect(calls, 1);
    api.close();
  });
}
