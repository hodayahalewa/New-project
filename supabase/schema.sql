-- מסע הערכים: מבנה הנתונים בענן (Supabase)
-- להדביק את כל הקובץ ב-SQL Editor של הפרויקט וללחוץ Run. אפשר להריץ שוב בלי נזק.

-- פרופיל לכל משתמש: שם, קוד הצטרפות מהמאמן, ותפקיד (מתאמן או מאמן)
create table if not exists public.profiles (
  id uuid primary key references auth.users (id) on delete cascade,
  name text,
  coach_code text,
  role text not null default 'trainee',
  created_at timestamptz not null default now()
);

-- מסע: כל ההתקדמות של המשחק נשמרת כמסמך אחד.
-- איפוס לא מוחק: המסע הקודם מסומן active = false ונשמר בארכיון.
create table if not exists public.journeys (
  id uuid primary key,
  user_id uuid not null references auth.users (id) on delete cascade,
  state jsonb not null,
  active boolean not null default true,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);
create index if not exists journeys_user_active on public.journeys (user_id, active);

-- הרשאות: כל משתמש רואה ומעדכן רק את הנתונים של עצמו.
-- (הרשאת צפייה למאמן תתווסף בשלב 5, לוח הבקרה.)
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
