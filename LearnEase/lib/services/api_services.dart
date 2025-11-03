// lib/services/api_service.dart
import 'dart:convert';
import 'package:flutter/foundation.dart' show kIsWeb;
import 'package:http/http.dart' as http;

/// Simple singleton API service with login/register helpers.
/// Update ports/paths if your backend differs.
class ApiService {
  // choose baseUrl depending on platform:
  ApiService._privateConstructor()
      : baseUrl = kIsWeb ? 'http://localhost:3000' : 'http://192.168.1.7:3000';

  static final ApiService instance = ApiService._privateConstructor();

  final String baseUrl;

  Map<String, String> _headers() => {
    'Accept': 'application/json',
    'Content-Type': 'application/json',
  };

  // -------------------------
  // Auth endpoints expected:
  // POST {baseUrl}/auth/register  -> body: {name,email,password}
  // POST {baseUrl}/auth/login     -> body: {email,password}
  // -------------------------

  Future<Map<String, dynamic>> register({
    required String name,
    required String email,
    required String password,
  }) async {
    final uri = Uri.parse('$baseUrl/auth/register');
    final res = await http.post(
      uri,
      headers: _headers(),
      body: jsonEncode({'name': name, 'email': email, 'password': password}),
    );
    return _handle(res);
  }

  Future<Map<String, dynamic>> login({
    required String email,
    required String password,
  }) async {
    final uri = Uri.parse('$baseUrl/auth/login');
    final res = await http.post(
      uri,
      headers: _headers(),
      body: jsonEncode({'email': email, 'password': password}),
    );
    return _handle(res);
  }

  // generic GET helper (optional)
  Future<Map<String, dynamic>> get(String path, {Map<String, String>? params}) async {
    final uri = Uri.parse('$baseUrl$path').replace(queryParameters: params);
    final res = await http.get(uri, headers: _headers());
    return _handle(res);
  }

  // generic POST helper (optional)
  Future<Map<String, dynamic>> post(String path, {Map<String, dynamic>? body}) async {
    final uri = Uri.parse('$baseUrl$path');
    final res = await http.post(uri, headers: _headers(), body: jsonEncode(body ?? {}));
    return _handle(res);
  }

  // -------------------------
  // Response handling
  // -------------------------
  Map<String, dynamic> _handle(http.Response res) {
    final int code = res.statusCode;
    final String raw = res.body.isEmpty ? '{}' : res.body;

    dynamic decoded;
    try {
      decoded = jsonDecode(raw);
    } catch (_) {
      decoded = null;
    }

    if (code >= 200 && code < 300) {
      if (decoded is Map<String, dynamic>) return decoded;
      return {'data': decoded};
    }

    // Non-success: produce friendly message
    String message = 'Server error ($code)';
    if (decoded is Map<String, dynamic>) {
      if (decoded.containsKey('message') && decoded['message'] != null) {
        message = decoded['message'].toString();
      } else if (decoded.containsKey('error') && decoded['error'] != null) {
        message = decoded['error'].toString();
      } else if (decoded.containsKey('errors') && decoded['errors'] != null) {
        message = decoded['errors'].toString();
      } else {
        message = decoded.toString();
      }
    } else if (raw.isNotEmpty) {
      message = raw;
    }

    throw Exception(message);
  }
}
