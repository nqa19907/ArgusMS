import 'models.dart';

// Demo data is never saved as a real pairing or reported as AI results.
JsonMap statusFixture({String camera = 'STOPPED', String ai = 'WARMUP'}) => {
  'schema_version': 1,
  'installation_id': 'installation-demo',
  'camera': {
    'id': 'living_room',
    'state': camera,
    'last_frame_age_ms': null,
    'reconnect_attempts': 0,
  },
  'ai': {
    'state': ai,
    'mode': 'mock',
    'model_id': 'mock-demo-v1',
    'processed_fps': 0,
    'last_inference_ms': 0,
    'warmup_remaining_samples': 30,
  },
  'notifications': {'configured': false, 'last_send_state': 'unavailable'},
};

JsonMap eventFixture() => {
  'schema_version': 1,
  'type': 'fall.confirmed',
  'event_id': 'evt-demo-${DateTime.now().microsecondsSinceEpoch}',
  'installation_id': 'installation-demo',
  'camera_id': 'living_room',
  'confirmed_at': DateTime.now().toUtc().toIso8601String(),
  'is_test': true,
  'message': 'Dữ liệu mẫu để kiểm tra UI, không phải kết quả AI.',
};
