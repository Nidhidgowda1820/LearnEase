CREATE TABLE IF NOT EXISTS public.quizzes (
  id SERIAL PRIMARY KEY,
  subject_code VARCHAR(16) NOT NULL,
  topic TEXT NOT NULL,
  question TEXT NOT NULL,
  options TEXT[],
  correct INTEGER NOT NULL,
  created_at TIMESTAMP DEFAULT NOW()
);
