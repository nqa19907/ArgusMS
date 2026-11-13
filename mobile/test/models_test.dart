import 'package:flutter_test/flutter_test.dart';
import 'package:mobile/config.dart';
import 'package:mobile/fixtures.dart';
import 'package:mobile/models.dart';

void main() {
  final pairingLink = Uri(
    scheme: 'fallguard',
    host: 'pair',
    queryParameters: {
      'server': 'http://10.0.2.2:8000',
      'code': 'test-code-only-1234',
      'installation': 'installation-demo',
    },
  ).toString();

  test('pairing URI matches backend.pairing.build_pairing_uri', () {
    final link = PairingLink.parse(pairingLink);
    expect(link.server.toString(), 'http://10.0.2.2:8000');
    expect(link.code, 'test-code-only-1234');
    expect(link.installationId, 'installation-demo');
  });
  test('reject missing/duplicate pairing fields and credentials in URL', () {
    expect(
      () => PairingLink.parse('fallguard://pair?server=http://localhost'),
      throwsFormatException,
    );
    expect(
      () => PairingLink.parse('$pairingLink&code=another-code'),
      throwsFormatException,
    );
    expect(
      () => parseServerUri('http://user:password@localhost:8000'),
      throwsFormatException,
    );
    expect(
      () => parseServerUri('http://localhost:8000/api'),
      throwsFormatException,
    );
    expect(
      () => parseServerUri('http://localhost:8000', allowHttp: false),
      throwsFormatException,
    );
  });
  test('camera connected does not imply AI ready', () {
    final status = SystemStatus.fromJson(
      statusFixture(camera: 'CONNECTED', ai: 'ERROR'),
    );
    expect(status.cameraState, 'CONNECTED');
    expect(status.aiState, 'ERROR');
    expect(status.lastFrameAgeMs, isNull);
  });
  test('reject wrong schema, malformed numeric status and unknown states', () {
    expect(
      () => SystemStatus.fromJson({...statusFixture(), 'schema_version': 2}),
      throwsFormatException,
    );
    final fixture = statusFixture();
    (fixture['ai'] as JsonMap)['processed_fps'] = '9.4';
    expect(() => SystemStatus.fromJson(fixture), throwsFormatException);
    expect(
      () => SystemStatus.fromJson(statusFixture(ai: 'MAGIC')),
      throwsFormatException,
    );
  });
  test('FCM minimal string payload parses false correctly', () {
    final event = FallEvent.fromPushData({
      'schema_version': '1',
      'type': 'fall.confirmed',
      'event_id': 'evt-test',
      'installation_id': 'installation-demo',
      'camera_id': 'living_room',
      'confirmed_at': '2026-11-12T01:00:00Z',
      'is_test': 'false',
    });
    expect(event.isTest, false);
    expect(event.message, contains('nghi ngã'));
  });
  test('invalid FCM boolean and missing event ID are rejected', () {
    expect(
      () => FallEvent.fromPushData({'schema_version': '1', 'is_test': '0'}),
      throwsFormatException,
    );
    final event = eventFixture()..remove('event_id');
    expect(() => FallEvent.fromJson(event), throwsFormatException);
  });
}
