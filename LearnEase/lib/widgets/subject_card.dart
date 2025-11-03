import 'package:flutter/material.dart';

class SubjectCard extends StatelessWidget {
  final String subjectName;
  final VoidCallback onTap;

  const SubjectCard({
    super.key,
    required this.subjectName,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 300),
        margin: const EdgeInsets.symmetric(vertical: 8, horizontal: 16),
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: Colors.indigo.shade50,
          borderRadius: BorderRadius.circular(16),
          border: Border.all(color: Colors.indigo.shade100),
          boxShadow: [
            BoxShadow(
              color: Colors.indigo.withValues(alpha: 0.08),
              blurRadius: 6,
              offset: const Offset(0, 3),
            ),
          ],
        ),
        child: Row(
          children: [
            const Icon(Icons.book_rounded, color: Colors.indigo, size: 30),
            const SizedBox(width: 12),
            Expanded(
              child: Text(
                subjectName,
                style: const TextStyle(
                  fontSize: 16,
                  fontWeight: FontWeight.w600,
                  color: Colors.black87,
                ),
              ),
            ),
            const Icon(Icons.arrow_forward_ios, size: 16, color: Colors.indigo),
          ],
        ),
      ),
    );
  }
}
