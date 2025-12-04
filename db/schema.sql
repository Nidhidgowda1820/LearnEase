-- user_files: per-user uploaded PDFs
create table if not exists user_files (
  id uuid primary key default gen_random_uuid(),
  user_id uuid references auth.users(id) on delete cascade,
  file_name text,
  storage_path text,
  file_type text,
  created_at timestamptz default now()
);

-- file_chunks: text chunks + embeddings for RAG
create table if not exists file_chunks (
  id uuid primary key default gen_random_uuid(),
  user_id uuid references auth.users(id) on delete cascade,
  file_id uuid references user_files(id) on delete cascade,
  chunk_index int,
  content text,
  embedding vector(1536),
  created_at timestamptz default now()
);

-- materials: shared notes / QPs / syllabus
create table if not exists materials (
  id uuid primary key default gen_random_uuid(),
  branch text,
  semester text,
  subject text,
  module text,
  type text, -- 'notes', 'qp', 'syllabus'
  title text,
  storage_path text,
  created_at timestamptz default now()
);

-- match_file_chunks: vector similarity search per user
create or replace function match_file_chunks(
  query_embedding vector(1536),
  match_count int,
  user_id_filter uuid
)
returns table (
  id uuid,
  file_id uuid,
  content text,
  similarity float
)
language sql stable as $$
  select
    file_chunks.id,
    file_chunks.file_id,
    file_chunks.content,
    1 - (file_chunks.embedding <=> query_embedding) as similarity
  from file_chunks
  where file_chunks.user_id = user_id_filter
  order by file_chunks.embedding <=> query_embedding
  limit match_count;
$$;
