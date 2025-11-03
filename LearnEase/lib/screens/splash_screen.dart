// lib/screens/splash_screen.dart
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/auth_provider.dart';

class SplashScreen extends StatefulWidget {
  const SplashScreen({Key? key}) : super(key: key);

  @override
  State<SplashScreen> createState() => _SplashScreenState();
}

class _SplashScreenState extends State<SplashScreen>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  late Animation<double> _fade;

  @override
  void initState() {
    super.initState();

    _controller = AnimationController(
      vsync: this,
      duration: const Duration(seconds: 1),
    )..forward();

    _fade = Tween<double>(begin: 0, end: 1).animate(_controller);

    _checkAuthAndNavigate();
  }

  Future<void> _checkAuthAndNavigate() async {
    await Future.delayed(const Duration(milliseconds: 700));

    final auth = Provider.of<AuthProvider>(context, listen: false);

    // optional delay for smoother animation
    await Future.delayed(const Duration(milliseconds: 250));

    // ✅ Avoid using context after dispose
    if (!mounted) return;

    if (auth.isLoggedIn) {
      Navigator.pushReplacementNamed(context, '/home');
    } else {
      Navigator.pushReplacementNamed(context, '/login');
    }
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final primary = Theme.of(context).colorScheme.primary;

    return Scaffold(
      backgroundColor: primary.withValues(alpha: 0.12), // ✅ replaced withOpacity()
      body: FadeTransition(
        opacity: _fade,
        child: Center(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Icon(Icons.school_rounded, size: 80, color: primary),
              const SizedBox(height: 16),
              Text(
                "Welcome to LearnHub",
                style: Theme.of(context)
                    .textTheme
                    .headlineSmall
                    ?.copyWith(color: primary),
              ),
              const SizedBox(height: 8),
              const CircularProgressIndicator(),
            ],
          ),
        ),
      ),
    );
  }
}
