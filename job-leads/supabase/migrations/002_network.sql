-- PEOPLE you want to connect with
create extension if not exists pgcrypto;
create extension if not exists pg_trgm;

create table if not exists public.people (
  id uuid primary key default gen_random_uuid(),
  platform text not null default 'linkedin',
  full_name text not null,
  headline text default '',
  company text default '',
  location text default '',
  profile_url text not null unique,
  tags text default '',
  source text default 'clipper',
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  notes text default ''
);

-- POSTS from those people (or public posts you want to reply on)
create table if not exists public.posts (
  id uuid primary key default gen_random_uuid(),
  platform text not null default 'linkedin',
  author_id uuid references public.people(id) on delete set null,
  url text not null unique,
  text text default '',
  hashtags text default '',
  posted_at timestamptz,
  meta jsonb default '{}'::jsonb,
  created_at timestamptz not null default now()
);

-- INTERACTIONS unify state across person/post/job
do $$ begin
  create type public.entity_type as enum ('person','post','job');
exception when duplicate_object then null; end $$;

create table if not exists public.interactions (
  id uuid primary key default gen_random_uuid(),
  entity_type public.entity_type not null,
  entity_id text not null,
  status text not null default 'Saved',
  score int not null default 0,
  pinned boolean not null default false,
  next_action text default '',
  next_action_date date,
  notes text default '',
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

-- TEMPLATES for invites/comments/cover letters
create table if not exists public.templates (
  id uuid primary key default gen_random_uuid(),
  kind text not null,
  title text not null,
  body text not null,
  created_at timestamptz not null default now()
);

-- SEARCH helper: materialized view + GIN index for FTS
create materialized view if not exists public.search_index as
select
  'person'::text as kind,
  id::text as rid,
  full_name as title,
  coalesce(company,'') as subtitle,
  coalesce(profile_url,'') as url,
  setweight(to_tsvector('english', coalesce(full_name,'')), 'A') ||
  setweight(to_tsvector('english', coalesce(headline,'')), 'B') ||
  setweight(to_tsvector('english', coalesce(company,'')), 'C') as doc,
  now() as refreshed_at
from people
union all
select
  'post',
  id::text,
  left(text, 80),
  coalesce(hashtags,''),
  url,
  setweight(to_tsvector('english', coalesce(text,'')), 'A'),
  now()
from posts
union all
select
  'job',
  id,
  title,
  coalesce(company,''),
  url,
  setweight(to_tsvector('english', coalesce(title,'')), 'A') ||
  setweight(to_tsvector('english', coalesce(description,'')), 'B') ||
  setweight(to_tsvector('english', coalesce(tags,'')), 'C'),
  now()
from jobs;

create index if not exists search_index_doc_idx on public.search_index using gin (doc);

-- RPC: search_all(q, limit)
create or replace function public.search_all(q text, lim int default 50)
returns table(kind text, rid text, title text, subtitle text, url text)
language sql stable as $$
  select kind, rid, title, subtitle, url
  from search_index
  where doc @@ plainto_tsquery('english', q)
  limit lim;
$$;

-- RLS: public read; writes via service role (your API)
alter table public.people enable row level security;
alter table public.posts enable row level security;
alter table public.interactions enable row level security;
alter table public.templates enable row level security;

create policy if not exists "public read" on public.people for select using (true);
create policy if not exists "public read" on public.posts for select using (true);
create policy if not exists "public read" on public.interactions for select using (true);
create policy if not exists "public read" on public.templates for select using (true);

