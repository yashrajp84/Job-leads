-- Enable extensions commonly used
create extension if not exists "uuid-ossp";

-- JOBS
create table if not exists public.jobs (
  id text primary key,                          -- sha1(url)
  title text not null,
  company text not null,
  location text default '',
  salary text default '',
  tags text default '',
  posted_at timestamptz,
  url text not null unique,
  source text not null,
  collected_at timestamptz not null default now(),
  description text default ''
);

-- LEADS (1:1 with jobs by id)
create table if not exists public.leads (
  id text primary key references public.jobs(id) on delete cascade,
  status text not null default 'Saved',         -- Saved | Applied | Interview | Offer | Rejected | On hold
  score int not null default 0,
  favourite boolean not null default false,
  resume_url text default '',
  cover_letter_url text default '',
  next_action text default '',
  next_action_date date,
  notes text default '',
  updated_at timestamptz not null default now()
);

-- Helpful indexes
create index if not exists jobs_source_idx on public.jobs (source);
create index if not exists jobs_collected_idx on public.jobs (collected_at desc);
create index if not exists leads_status_idx on public.leads (status);
create index if not exists leads_next_action_date_idx on public.leads (next_action_date);

-- Row Level Security
alter table public.jobs enable row level security;
alter table public.leads enable row level security;

-- Policies:
-- 1) Anonymous can read jobs (public listing) and leads (read-only for dashboard previews)
create policy "public read jobs" on public.jobs
for select using (true);

create policy "public read leads" on public.leads
for select using (true);

-- 2) Service role can do anything (bypasses RLS automatically).
-- (No explicit policy needed; service role bypasses RLS)

