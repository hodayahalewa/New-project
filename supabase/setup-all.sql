-- מסע הערכים: כל הטבלאות בבת אחת (schema.sql + schema-reminders.sql). אפשר להריץ שוב בלי נזק.

create table if not exists public.profiles (
  id uuid primary key references auth.users (id) on delete cascade,
  name text,
  coach_code text,
  role text not null default 'trainee',
  created_at timestamptz not null default now()
);

create table if not exists public.journeys (
  id uuid primary key,
  user_id uuid not null references auth.users (id) on delete cascade,
  state jsonb not null,
  active boolean not null default true,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);
create index if not exists journeys_user_active on public.journeys (user_id, active);

alter table public.profiles enable row level security;
alter table public.journeys enable row level security;

drop policy if exists "own profile" on public.profiles;
create policy "own profile" on public.profiles
  for all to authenticated
  using ((select auth.uid()) = id)
  with check ((select auth.uid()) = id);

drop policy if exists "own journeys" on public.journeys;
create policy "own journeys" on public.journeys
  for all to authenticated
  using ((select auth.uid()) = user_id)
  with check ((select auth.uid()) = user_id);

grant select, insert, update on public.profiles to authenticated;
grant select, insert, update on public.journeys to authenticated;

alter table public.profiles
  add column if not exists tz text not null default 'Asia/Jerusalem',
  add column if not exists push_enabled boolean not null default false,
  add column if not exists reminder_day smallint,
  add column if not exists reminder_time text,
  add column if not exists next_challenge_value text,
  add column if not exists next_challenge text,
  add column if not exists challenges_done integer not null default 0,
  add column if not exists last_sent_on date,
  add column if not exists last_sent_challenges integer,
  add column if not exists nudged_for date;

create table if not exists public.push_subscriptions (
  endpoint text primary key,
  user_id uuid not null references auth.users (id) on delete cascade,
  p256dh text not null,
  auth text not null,
  created_at timestamptz not null default now()
);
create index if not exists push_subscriptions_user on public.push_subscriptions (user_id);
alter table public.push_subscriptions enable row level security;
drop policy if exists "own push subscriptions" on public.push_subscriptions;
create policy "own push subscriptions" on public.push_subscriptions
  for all to authenticated
  using ((select auth.uid()) = user_id)
  with check ((select auth.uid()) = user_id);
grant select, insert, update, delete on public.push_subscriptions to authenticated;
