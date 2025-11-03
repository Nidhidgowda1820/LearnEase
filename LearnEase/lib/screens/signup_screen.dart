// lib/screens/signup_screen.dart
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../widgets/custom_textfield.dart';
import '../widgets/custom_button.dart';
import '../providers/auth_provider.dart';

class SignupScreen extends StatefulWidget {
  const SignupScreen({super.key});
  @override
  State<SignupScreen> createState() => _SignupScreenState();
}

class _SignupScreenState extends State<SignupScreen> with SingleTickerProviderStateMixin {
  final _formKey = GlobalKey<FormState>();
  final _name = TextEditingController();
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
    _name.dispose();
    _email.dispose();
    _pass.dispose();
    super.dispose();
  }

  Future<void> _submit() async {
    if (!_formKey.currentState!.validate()) return;
    final auth = context.read<AuthProvider>();
    try {
      await auth.register(name: _name.text.trim(), email: _email.text.trim(), password: _pass.text.trim());
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
      appBar: AppBar(title: const Text('Create account'), backgroundColor: Colors.indigo[600]),
      body: FadeTransition(
        opacity: _fade,
        child: SafeArea(
          child: SingleChildScrollView(
            padding: const EdgeInsets.all(18),
            child: Form(
              key: _formKey,
              child: Column(
                children: [
                  CustomTextField(controller: _name, hintText: 'Full name', icon: Icons.person),
                  CustomTextField(controller: _email, hintText: 'Email', icon: Icons.email_outlined),
                  CustomTextField(controller: _pass, hintText: 'Password', icon: Icons.lock_outline, isPassword: true),
                  const SizedBox(height: 18),
                  auth.loading ? const CircularProgressIndicator() : CustomButton(text: 'Sign Up', onPressed: _submit),
                  const SizedBox(height: 12),
                  TextButton(onPressed: () => Navigator.pop(context), child: const Text('Already have account? Sign In')),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }
}
