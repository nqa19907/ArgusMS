import 'package:flutter/foundation.dart';

class AppConfig {
  static const schemaVersion = 1;
  static const requestTimeout = Duration(seconds: 10);
  static const statusInterval = Duration(seconds: 5);
}

Uri parseServerUri(String value, {bool allowHttp = kDebugMode}) {
  final uri = Uri.tryParse(value.trim());
  if (uri == null ||
      !uri.hasAuthority ||
      uri.host.isEmpty ||
      !['http', 'https'].contains(uri.scheme) ||
      uri.userInfo.isNotEmpty ||
      uri.hasQuery ||
      uri.hasFragment ||
      (uri.path.isNotEmpty && uri.path != '/')) {
    throw const FormatException(
      'Địa chỉ backend phải dạng https://host:port, không có đường dẫn hoặc mật khẩu.',
    );
  }
  if (!allowHttp && uri.scheme == 'http') {
    throw const FormatException(
      'HTTP chỉ dùng trong APK debug trên mạng lab. Bản release cần HTTPS.',
    );
  }
  return uri.replace(path: '');
}

class PairingLink {
  const PairingLink(this.server, this.code, this.installationId);

  final Uri server;
  final String code;
  final String installationId;

  factory PairingLink.parse(String value) {
    final uri = Uri.tryParse(value.trim());
    if (uri == null ||
        uri.scheme != 'fallguard' ||
        uri.host != 'pair' ||
        uri.path.isNotEmpty ||
        uri.hasFragment ||
        uri.userInfo.isNotEmpty) {
      throw const FormatException(
        'Dán link fallguard://pair?... do backend tạo.',
      );
    }
    String field(String key) {
      final values = uri.queryParametersAll[key];
      if (values == null ||
          values.length != 1 ||
          values.single.trim().isEmpty) {
        throw FormatException('Link ghép thiếu hoặc lặp trường $key.');
      }
      return values.single;
    }

    final server = parseServerUri(field('server'));
    final code = field('code');
    final installation = field('installation');
    if (code.length < 10 || code.length > 256 || installation.length > 128) {
      throw const FormatException(
        'Mã ghép hoặc installation không hợp lệ. Hãy tạo link mới.',
      );
    }
    return PairingLink(server, code, installation);
  }
}
