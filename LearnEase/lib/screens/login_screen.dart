// lib/screens/login_screen.dart
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../widgets/custom_textfield.dart';
import '../widgets/custom_button.dart';
import '../providers/auth_provider.dart';

class LoginScreen extends StatefulWidget {
  const LoginScreen({super.key});
  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> with SingleTickerProviderStateMixin {
  final _formKey = GlobalKey<FormState>();
  final _email = TextEditingController();
  final _pass = TextEditingController();
  late AnimationController _ani;
  late Animation<double> _fade;

  @override
  void initState() {
    super.initState();
    _ani = AnimationController(vsync: this, duration: const Duration(milliseconds: 700));
    _fade = CurvedAnimation(parent: _ani, curve: Curves.easeIn);
    _ani.forward();
  }

  @override
  void dispose() {
    _ani.dispose();
    _email.dispose();
    _pass.dispose();
    super.dispose();
  }

  Future<void> _submit() async {
    if (!_formKey.currentState!.validate()) return;
    final auth = context.read<AuthProvider>();
    try {
      await auth.login(email: _email.text.trim(), password: _pass.text.trim());
      if (mounted) Navigator.pushReplacementNamed(context, '/home');
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(e.toString())));
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final auth = context.watch<AuthProvider>();

    return Scaffold(
      body: FadeTransition(
        opacity: _fade,
        child: SafeArea(
          child: Center(
            child: SingleChildScrollView(
              padding: const EdgeInsets.all(22),
              child: Column(
                children: [
                  Icon(Icons.school, size: 86, color: Colors.indigo[600]),
                  const SizedBox(height: 18),
                  const Text('Welcome back', style: TextStyle(fontSize: 22, fontWeight: FontWeight.bold, color: Colors.indigo)),
                  const SizedBox(height: 8),
                  const Text('Sign in to continue', style: TextStyle(color: Colors.black54)),
                  const SizedBox(height: 28),
                  Form(
                    key: _formKey,
                    child: Column(
                      children: [
                        CustomTextField(controller: _email, hintText: 'Email', icon: Icons.email_outlined),
                        CustomTextField(controller: _pass, hintText: 'Password', icon: Icons.lock_outline, isPassword: true),
                        const SizedBox(height: 18),
                        auth.loading
                            ? const CircularProgressIndicator()
                            : CustomButton(text: 'Sign In', onPressed: _submit),
                        const SizedBox(height: 12),
                        TextButton(
                          onPressed: () => Navigator.pushNamed(context, '/signup'),
                          child: const Text("Don't have an account? Sign up"),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }
}
