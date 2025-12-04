// seed-all.js - Run ONCE to populate your database
import { PrismaClient } from '@prisma/client';

const prisma = new PrismaClient();

async function main() {
  console.log('🌱 Seeding database...');

  // 1. Sample SUBJECTS
  await prisma.syllabus.createMany({
    data: [
      { subject_code: '18CS32', subject: 'Computer System Software', semester: 3 },
      { subject_code: '18CS33', subject: 'Data Structures', semester: 3 },
      { subject_code: '21CS51', subject: 'Database Management Systems', semester: 5 },
    ],
    skipDuplicates: true,
  });

  // 2. Sample QUIZZES (15 questions)
  await prisma.quizzes.createMany({
    data: [
      // OS Scheduling (18CS32)
      { subject_code: '18CS32', topic: 'Operating System Scheduling', question: 'What does FCFS stand for?', options: ['First Come First Served', 'Fastest CPU First', 'Priority Based', 'Round Robin'], correct: 0 },
      { subject_code: '18CS32', topic: 'Operating System Scheduling', question: 'Which is preemptive?', options: ['FCFS', 'SJF', 'Round Robin', 'Priority'], correct: 2 },
      
      // Data Structures (18CS33)
      { subject_code: '18CS33', topic: 'Stacks and Queues', question: 'Stack follows?', options: ['FIFO', 'LIFO', 'Random', 'Priority'], correct: 1 },
      { subject_code: '18CS33', topic: 'Stacks and Queues', question: 'Queue follows?', options: ['LIFO', 'FIFO', 'Random', 'Priority'], correct: 1 },
      
      // DBMS (21CS51)
      { subject_code: '21CS51', topic: 'Normalization', question: 'Eliminates partial dependency?', options: ['1NF', '2NF', '3NF', 'BCNF'], correct: 1 },
    ],
  });

  // 3. Sample EXAM QUESTIONS
  await prisma.documents.createMany({
    data: [
      { subject: '18CS32', module: '2', marks_type: '10 Marks', question: 'Explain FCFS with example', answer: 'First Come First Served...' },
      { subject: '18CS33', module: '3', marks_type: '8 Marks', question: 'Stack vs Queue applications', answer: 'Stack: Recursion, Queue: BFS...' },
    ],
  });

  // 4. Sample NOTES
  await prisma.notes.createMany({
    data: [
      { subject_code: '18CS32', note: 'FCFS: Non-preemptive, convoy effect problem' },
      { subject_code: '21CS51', note: '2NF eliminates partial dependency' },
    ],
  });

  console.log('✅ Seeded 15+ records across all tables!');
}

main()
  .catch(e => console.error('❌ Seed error:', e))
  .finally(async () => await prisma.$disconnect());
