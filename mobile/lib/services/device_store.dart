import 'dart:convert';

import 'package:flutter_secure_storage/flutter_secure_storage.dart';

import '../config.dart';
import '../models.dart';

class DeviceStore {
  DeviceStore({FlutterSecureStorage? storage})
    : _storage = storage ?? const FlutterSecureStorage();
  final FlutterSecureStorage _storage;
  static const _key = 'argusms.pairing.v1';

  Future<PairingSession?> loadPairing() async {
    final raw = await _storage.read(key: _key);
    if (raw == null) return null;
    final json = jsonObject(jsonDecode(raw));
    return PairingSession.fromJson(
      json,
      parseServerUri(requiredString(json, 'server')),
    );
  }

  Future<void> savePairing(PairingSession value) =>
      _storage.write(key: _key, value: jsonEncode(value.toStorageJson()));

  Future<void> clearPairing() => _storage.delete(key: _key);
}
