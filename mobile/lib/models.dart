import 'config.dart';

typedef JsonMap = Map<String, dynamic>;

JsonMap jsonObject(Object? value) {
  if (value is! Map<String, dynamic>) {
    throw const FormatException('Dữ liệu phải là JSON object.');
  }
  return value;
}

void checkSchema(JsonMap json) {
  if (json['schema_version'] != AppConfig.schemaVersion) {
    throw const FormatException(
      'schema_version không tương thích (app hỗ trợ 1).',
    );
  }
}

String requiredString(JsonMap json, String key) {
  final value = json[key];
  if (value is! String || value.trim().isEmpty) {
    throw FormatException('Thiếu hoặc sai kiểu trường $key.');
  }
  return value;
}

class PairingSession {
  const PairingSession({
    required this.server,
    required this.deviceId,
    required this.deviceSecret,
    required this.installationId,
  });

  final Uri server;
  final String deviceId;
  final String deviceSecret;
  final String installationId;

  factory PairingSession.fromJson(JsonMap json, Uri server) {
    checkSchema(json);
    return PairingSession(
      server: server,
      deviceId: requiredString(json, 'device_id'),
      deviceSecret: requiredString(json, 'device_secret'),
      installationId: requiredString(json, 'installation_id'),
    );
  }

  JsonMap toStorageJson() => {
    'schema_version': 1,
    'server': server.toString(),
    'device_id': deviceId,
    'device_secret': deviceSecret,
    'installation_id': installationId,
  };
}

class SystemStatus {
  const SystemStatus({
    required this.installationId,
    required this.cameraId,
    required this.cameraState,
    required this.aiState,
    required this.aiMode,
    required this.modelId,
    required this.processedFps,
    required this.notificationsConfigured,
    required this.lastSendState,
    this.lastFrameAgeMs,
  });

  final String installationId;
  final String cameraId;
  final String cameraState;
  final String aiState;
  final String aiMode;
  final String modelId;
  final double processedFps;
  final bool notificationsConfigured;
  final String lastSendState;
  final int? lastFrameAgeMs;

  factory SystemStatus.fromJson(JsonMap json) {
    checkSchema(json);
    final camera = jsonObject(json['camera']);
    final ai = jsonObject(json['ai']);
    final push = jsonObject(json['notifications']);
    final cameraState = requiredString(camera, 'state');
    final aiState = requiredString(ai, 'state');
    if (![
          'STOPPED',
          'CONNECTING',
          'CONNECTED',
          'RECONNECTING',
          'ERROR',
        ].contains(cameraState) ||
        ![
          'LOADING',
          'WARMUP',
          'READY',
          'DEGRADED',
          'ERROR',
        ].contains(aiState)) {
      throw const FormatException('Trạng thái camera/AI chưa được app hỗ trợ.');
    }
    final fps = ai['processed_fps'];
    final age = camera['last_frame_age_ms'];
    if (fps is! num ||
        !fps.isFinite ||
        fps < 0 ||
        (age != null && (age is! int || age < 0)) ||
        push['configured'] is! bool) {
      throw const FormatException('Sai kiểu dữ liệu status.');
    }
    return SystemStatus(
      installationId: requiredString(json, 'installation_id'),
      cameraId: requiredString(camera, 'id'),
      cameraState: cameraState,
      aiState: aiState,
      aiMode: requiredString(ai, 'mode'),
      modelId: requiredString(ai, 'model_id'),
      processedFps: fps.toDouble(),
      lastFrameAgeMs: age as int?,
      notificationsConfigured: push['configured'] as bool,
      lastSendState: requiredString(push, 'last_send_state'),
    );
  }
}

class FallEvent {
  const FallEvent({
    required this.eventId,
    required this.installationId,
    required this.cameraId,
    required this.confirmedAt,
    required this.isTest,
    required this.message,
  });

  final String eventId;
  final String installationId;
  final String cameraId;
  final DateTime confirmedAt;
  final bool isTest;
  final String message;

  factory FallEvent.fromJson(JsonMap json) {
    checkSchema(json);
    if (json['type'] != 'fall.confirmed' || json['is_test'] is! bool) {
      throw const FormatException('Sai loại sự kiện hoặc is_test.');
    }
    final time = DateTime.tryParse(requiredString(json, 'confirmed_at'));
    if (time == null) throw const FormatException('confirmed_at không hợp lệ.');
    return FallEvent(
      eventId: requiredString(json, 'event_id'),
      installationId: requiredString(json, 'installation_id'),
      cameraId: requiredString(json, 'camera_id'),
      confirmedAt: time,
      isTest: json['is_test'] as bool,
      message: json['message'] is String
          ? json['message'] as String
          : (json['is_test'] == true
                ? 'Thông báo thử kết nối.'
                : 'Có sự kiện nghi ngã. Vui lòng kiểm tra.'),
    );
  }

  factory FallEvent.fromPushData(JsonMap data) {
    // FCM data values are strings; do not cast "false" to bool.
    if (data['schema_version'] != '1' ||
        !['true', 'false'].contains(data['is_test'])) {
      throw const FormatException('Payload FCM sai schema_version/is_test.');
    }
    return FallEvent.fromJson({
      ...data,
      'schema_version': 1,
      'is_test': data['is_test'] == 'true',
    });
  }
}
