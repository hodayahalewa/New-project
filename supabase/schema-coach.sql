-- מסע הערכים: לוח המאמן (שלב 5)
-- להדביק ב-SQL Editor וללחוץ Run. אפשר להריץ שוב בלי נזק.

-- 1. מה המאמן יכול לראות: סיכום בלבד. טבלת journeys נשארת פרטית למתאמן.
alter table public.profiles
  add column if not exists email text,
  add column if not exists summary jsonb,
  add column if not exists share_reflections boolean not null default false,
  add column if not exists last_active timestamptz;

-- 2. מתאמן לא יכול להפוך את עצמו למאמן: התפקיד (role) נקבע רק מכאן, מה-SQL Editor.
revoke insert, update on public.profiles from authenticated;
grant insert (id, name, coach_code, email, summary, share_reflections, last_active, tz, push_enabled,
              reminder_day, reminder_time, next_challenge_value, next_challenge, challenges_done)
  on public.profiles to authenticated;
grant update (id, name, coach_code, email, summary, share_reflections, last_active, tz, push_enabled,
              reminder_day, reminder_time, next_challenge_value, next_challenge, challenges_done)
  on public.profiles to authenticated;

-- 3. קודי הצטרפות של המאמן
create table if not exists public.coach_codes (
  code text primary key,
  coach_id uuid not null references auth.users (id) on delete cascade,
  created_at timestamptz not null default now()
);
alter table public.coach_codes enable row level security;

create or replace function public.is_coach() returns boolean
language sql stable security definer set search_path = '' as $$
  select exists (select 1 from public.profiles where id = (select auth.uid()) and role = 'coach');
$$;

drop policy if exists "coach manages own codes" on public.coach_codes;
create policy "coach manages own codes" on public.coach_codes
  for all to authenticated
  using (coach_id = (select auth.uid()))
  with check (coach_id = (select auth.uid()) and public.is_coach());
grant select, insert, delete on public.coach_codes to authenticated;

-- בדיקה אם קוד קיים (בלי לחשוף של מי הוא)
create or replace function public.code_exists(c text) returns boolean
language sql stable security definer set search_path = '' as $$
  select exists (select 1 from public.coach_codes where upper(code) = upper(trim(c)));
$$;
grant execute on function public.code_exists(text) to anon, authenticated;

-- 4. המאמן רואה את הפרופיל (והסיכום) של מי שהצטרף עם אחד הקודים שלו
drop policy if exists "coach reads trainees" on public.profiles;
create policy "coach reads trainees" on public.profiles
  for select to authenticated
  using (upper(coach_code) in (select upper(code) from public.coach_codes where coach_id = (select auth.uid())));

-- 5. הגדרת המאמן: להחליף את הכתובת במייל של המאמן, ולהריץ (פעם אחת לכל מאמן)
-- insert into public.profiles (id, role)
--   select id, 'coach' from auth.users where email = 'COACH_EMAIL_HERE'
--   on conflict (id) do update set role = 'coach';
