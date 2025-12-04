import prisma from './src/config/db.js';

async function main() {
  await prisma.$executeRaw`
    CREATE TABLE IF NOT EXISTS public.quizzes (
      id SERIAL PRIMARY KEY,
      subject_code VARCHAR(16) NOT NULL,
      topic TEXT NOT NULL,
      question TEXT NOT NULL,
      options TEXT[],
      correct INTEGER NOT NULL,
      created_at TIMESTAMP DEFAULT NOW()
    );
  `;
  console.log('✅ Quizzes table created!');
}

main().finally(() => prisma.$disconnect());
