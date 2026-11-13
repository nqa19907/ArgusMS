import 'dart:async';
import 'dart:convert';
import 'dart:io';

import 'package:http/http.dart' as http;

import '../config.dart';
import '../models.dart';

class ApiException implements Exception {
  const ApiException(this.message, {this.statusCode});
  final String message;
  final int? statusCode;
  bool get unauthorized => statusCode == 401 || statusCode == 403;
  @override
  String toString() => message;
}

class ApiClient {
  ApiClient({http.Client? client, this.timeout = AppConfig.requestTimeout})
    : _client = client ?? http.Client();
  final http.Client _client;
  final Duration timeout;

  Future<JsonMap> _request(
    Uri server,
    String method,
    String path, {
    String? secret,
    JsonMap? body,
    bool claim = false,
  }) async {
    try {
      final request = http.Request(method, server.resolve(path));
      request.headers['Accept'] = 'application/json';
      if (secret != null) request.headers['Authorization'] = 'Bearer $secret';
      if (body != null) {
        request.headers['Content-Type'] = 'application/json';
        request.body = jsonEncode(body);
      }
      final response = await (() async {
        final streamed = await _client.send(request);
        return http.Response.fromStream(streamed);
      })().timeout(timeout);
      if (response.statusCode < 200 || response.statusCode >= 300) {
        final message = switch (response.statusCode) {
          400 => 'Dữ liệu không hợp lệ hoặc link ghép không đúng backend.',
          401 ||
          403 => 'Khóa thiết bị không hợp lệ hoặc đã bị thu hồi. Hãy ghép lại.',
          404 =>
            'Backend chưa có API này; kiểm tra nhánh develop và hợp đồng SV2.',
          409 => 'Mã ghép đã được dùng. Nhờ SV2 tạo link mới.',
          410 => 'Mã ghép hết hạn. Nhờ SV2 tạo link mới.',
          422 => 'Dữ liệu gửi chưa đúng schema của backend.',
          429 => 'Quá nhiều yêu cầu. Chờ rồi thử lại.',
          _ => 'Backend trả HTTP ${response.statusCode}.',
        };
        throw ApiException(message, statusCode: response.statusCode);
      }
      if (response.statusCode == 204) return <String, dynamic>{};
      return jsonObject(jsonDecode(utf8.decode(response.bodyBytes)));
    } on TimeoutException {
      throw ApiException(
        claim
            ? 'Claim bị timeout; code có thể đã được dùng. Tạo link mới, không tự retry claim.'
            : 'Backend phản hồi quá chậm. Kiểm tra mạng và server.',
      );
    } on SocketException {
      throw ApiException(
        claim
            ? 'Mất kết nối khi claim. Tạo link mới nếu chưa rõ code đã được dùng chưa.'
            : 'Không kết nối được backend. Kiểm tra IP, mạng và server.',
      );
    } on http.ClientException {
      throw const ApiException(
        'Kết nối HTTP thất bại. Kiểm tra địa chỉ và mạng.',
      );
    }
  }

  Future<void> health(Uri server) async {
    final json = await _request(server, 'GET', '/health');
    checkSchema(json);
    if (json['status'] != 'alive') {
      throw const FormatException('Health response không đúng contract SV2.');
    }
  }

  Future<PairingSession> pair(PairingLink link) async {
    final json = await _request(
      link.server,
      'POST',
      '/api/v1/pairing/claim',
      claim: true,
      body: {
        'pairing_code': link.code,
        'expected_installation_id': link.installationId,
        'client_label': 'ArgusMS Android SV3',
      },
    );
    final session = PairingSession.fromJson(json, link.server);
    if (session.installationId != link.installationId) {
      throw const FormatException(
        'Backend trả installation khác link ghép. Không lưu khóa.',
      );
    }
    return session;
  }

  Future<SystemStatus> getStatus(PairingSession session) async {
    final json = await _request(
      session.server,
      'GET',
      '/api/v1/status',
      secret: session.deviceSecret,
    );
    final result = SystemStatus.fromJson(json);
    if (result.installationId != session.installationId) {
      throw const ApiException(
        'Backend đã thay installation. Cần ghép lại.',
        statusCode: 401,
      );
    }
    return result;
  }

  Future<void> registerPush(PairingSession session, String token) async {
    final json = await _request(
      session.server,
      'PUT',
      '/api/v1/devices/${Uri.encodeComponent(session.deviceId)}/push',
      secret: session.deviceSecret,
      body: {'push_kind': 'fcm', 'push_value': token, 'sound_enabled': true},
    );
    checkSchema(json);
    if (json['updated'] != true || json['device_id'] != session.deviceId) {
      throw const FormatException(
        'Backend chưa xác nhận đăng ký push đúng thiết bị.',
      );
    }
  }

  Future<String> sendTest(PairingSession session) async {
    final json = await _request(
      session.server,
      'POST',
      '/api/v1/notifications/test',
      secret: session.deviceSecret,
    );
    checkSchema(json);
    if (json['is_test'] != true) {
      throw const FormatException('Response test thiếu nhãn thử.');
    }
    return requiredString(json, 'event_id');
  }

  Future<void> revoke(PairingSession session) async {
    await _request(
      session.server,
      'DELETE',
      '/api/v1/devices/${Uri.encodeComponent(session.deviceId)}',
      secret: session.deviceSecret,
    );
  }

  void close() => _client.close();
}
