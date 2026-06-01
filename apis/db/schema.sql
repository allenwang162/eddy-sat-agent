-- Target Postgres schema for the next database-backed data layer.
-- The current prototype uses file repositories behind service boundaries.

create table if not exists users (
  id text primary key,
  name text not null,
  email text not null unique,
  password_salt text not null,
  password_hash text not null,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists sessions (
  token text primary key,
  user_id text not null references users(id) on delete cascade,
  created_at timestamptz not null default now(),
  expires_at timestamptz not null
);

create table if not exists oauth_tokens (
  id bigserial primary key,
  user_id text not null references users(id) on delete cascade,
  provider text not null,
  encrypted_payload jsonb not null,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique (user_id, provider)
);

create table if not exists question_bank_items (
  id text primary key,
  section text not null,
  module text,
  type text not null,
  difficulty text,
  concept text not null,
  skill text,
  prompt text not null,
  choices jsonb not null,
  answer text not null,
  explanation text,
  logic text,
  tutorial text,
  source text,
  metadata jsonb not null default '{}'::jsonb
);

create table if not exists exam_bundles (
  id text primary key,
  title text not null,
  section text not null,
  source text,
  status text not null default 'available',
  metadata jsonb not null default '{}'::jsonb
);

create table if not exists exam_bundle_questions (
  bundle_id text not null references exam_bundles(id) on delete cascade,
  question_id text not null references question_bank_items(id) on delete cascade,
  position integer not null,
  primary key (bundle_id, question_id)
);

create table if not exists exam_scoring_tables (
  id text primary key,
  practice_test integer not null,
  score_type text not null,
  payload jsonb not null,
  source text,
  created_at timestamptz not null default now()
);

create table if not exists attempts (
  id text primary key,
  user_id text not null references users(id) on delete cascade,
  bundle_id text,
  score integer not null,
  correct integer not null,
  total integer not null,
  duration_ms integer,
  started_at timestamptz,
  completed_at timestamptz not null default now()
);

create table if not exists attempt_answers (
  id bigserial primary key,
  attempt_id text not null references attempts(id) on delete cascade,
  question_id text not null,
  selected text,
  correct_answer text not null,
  is_correct boolean not null,
  concept text not null,
  skill text
);

create index if not exists idx_attempts_user_completed on attempts(user_id, completed_at desc);
create index if not exists idx_attempt_answers_attempt on attempt_answers(attempt_id);
create index if not exists idx_question_concept on question_bank_items(concept);
