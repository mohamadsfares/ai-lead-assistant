-- 1. Turn on pgvector (adds the vector type)
create extension if not exists vector;

-- 2. Table: one row per chunk (RLS enabled)
create table chunks (
  id bigserial primary key,
  source text not null,
  section text not null,
  content text not null,
  embedding vector(1536)
);

alter table chunks enable row level security;

-- 3. Search: return the chunks closest in meaning to the question
create or replace function match_chunks(
  query_embedding vector(1536),
  match_count int
)
returns table (
  id bigint,
  source text,
  section text,
  content text,
  similarity float
)
language sql
as $$
  select id, source, section, content,
         1 - (embedding <=> query_embedding) as similarity
  from chunks
  order by embedding <=> query_embedding
  limit match_count;
$$;

-- 4. Request logs: one row per API request (tokens, cost, latency)
create table request_logs (
  id bigserial primary key,
  created_at timestamptz not null default now(),
  endpoint text not null,
  latency_s float not null,
  input_tokens int not null,
  output_tokens int not null,
  cost_usd float not null,
  outcome text
);

alter table request_logs enable row level security;