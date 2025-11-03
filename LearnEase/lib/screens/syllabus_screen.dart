import 'package:flutter/material.dart';

class SyllabusScreen extends StatelessWidget {
  const SyllabusScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final semesters = {
      "5th Semester": ["Database Management Systems", "Computer Networks", "Automata Theory", "Software Engineering"],
      "6th Semester": ["Web Technology", "Machine Learning", "Compiler Design", "Cloud Computing"],
    };

    return Scaffold(
      appBar: AppBar(
        title: const Text("Syllabus", style: TextStyle(fontWeight: FontWeight.bold)),
        backgroundColor: Colors.indigo[600],
        foregroundColor: Colors.white,
      ),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: semesters.entries.map((entry) {
          return Card(
            elevation: 4,
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
            margin: const EdgeInsets.symmetric(vertical: 8),
            child: ExpansionTile(
              title: Text(entry.key, style: const TextStyle(fontWeight: FontWeight.bold, color: Colors.indigo)),
              children: entry.value
                  .map((subject) => ListTile(title: Text(subject), leading: const Icon(Icons.book_outlined)))
                  .toList(),
            ),
          );
        }).toList(),
      ),
    );
  }
}
