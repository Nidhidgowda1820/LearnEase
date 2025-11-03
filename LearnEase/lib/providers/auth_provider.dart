// lib/providers/auth_provider.dart
import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../services/api_services.dart';

class AuthProvider extends ChangeNotifier {
  final ApiService _api = ApiService.instance;

  bool _loading = false;
  bool get loading => _loading;

  Map<String, dynamic>? _user;
  Map<String, dynamic>? get user => _user;

  bool get isLoggedIn => _user != null;

  // Load user from local storage on app start
  Future<void> loadUserFromStorage() async {
    final prefs = await SharedPreferences.getInstance();
    final email = prefs.getString('email');
    final name = prefs.getString('name');
    if (email != null) {
      _user = {'email': email, 'name': name ?? 'User'};
      notifyListeners();
    }
  }

  Future<void> login({
    required String email,
    required String password,
  }) async {
    try {
      _loading = true;
      notifyListeners();
      final resp = await _api.login(email: email, password: password);
      _user = resp['user'] as Map<String, dynamic>? ?? {'email': email};

      // Save user info
      final prefs = await SharedPreferences.getInstance();
      await prefs.setString('email', email);
      await prefs.setString('name', _user?['name'] ?? '');
    } catch (e) {
      rethrow;
    } finally {
      _loading = false;
      notifyListeners();
    }
  }

  Future<void> register({
    required String name,
    required String email,
    required String password,
  }) async {
    try {
      _loading = true;
      notifyListeners();
      final resp = await _api.register(name: name, email: email, password: password);
      _user = resp['user'] as Map<String, dynamic>? ?? {'name': name, 'email': email};

      final prefs = await SharedPreferences.getInstance();
      await prefs.setString('email', email);
      await prefs.setString('name', name);
    } catch (e) {
      rethrow;
    } finally {
      _loading = false;
      notifyListeners();
    }
  }

  Future<void> logout() async {
    _user = null;
    final prefs = await SharedPreferences.getInstance();
    await prefs.clear();
    notifyListeners();
  }
}
