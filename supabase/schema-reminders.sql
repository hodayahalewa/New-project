-- מסע הערכים: תזכורות לאתגר השבועי (שלב 4)
-- להדביק ב-SQL Editor וללחוץ Run, אחרי schema.sql. אפשר להריץ שוב בלי נזק.

-- הגדרות התזכורת של כל מתאמן, והאתגר הבא שלו (האפליקציה מעדכנת אותם)
alter table public.profiles
  add column if not exists tz text not null default 'Asia/Jerusalem',
  add column if not exists push_enabled boolean not null default false,
  add column if not exists reminder_day smallint,          -- 0 = ראשון ... 6 = שבת
  add column if not exists reminder_time text,             -- "HH:MM"
  add column if not exists next_challenge_value text,
  add column if not exists next_challenge text,
  add column if not exists challenges_done integer not null default 0,
  add column if not exists last_sent_on date,
  add column if not exists last_sent_challenges integer,
  add column if not exists nudged_for date;

-- המכשירים שאישרו התראות (טלפון, מחשב)
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
