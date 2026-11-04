-- מסע הערכים: הפעלת בדיקת התזכורות כל 15 דקות
-- להריץ ב-SQL Editor רק אחרי שהפונקציה send-reminders פורסמה.
-- להחליף את PASTE_CRON_SECRET_HERE בקוד הסודי (CRON_SECRET) שנשמר ב-Secrets של הפונקציה.

create extension if not exists pg_cron;
create extension if not exists pg_net;

-- אם כבר קיים תזמון בשם הזה, מוחקים אותו ויוצרים מחדש
select cron.unschedule('masa-send-reminders') where exists (select 1 from cron.job where jobname = 'masa-send-reminders');

select cron.schedule(
  'masa-send-reminders',
  '*/15 * * * *',
  $$
  select net.http_post(
    url := 'https://jilxleducctilebsvtlp.supabase.co/functions/v1/send-reminders',
    headers := jsonb_build_object('Content-Type', 'application/json', 'x-cron-secret', 'PASTE_CRON_SECRET_HERE'),
    body := '{}'::jsonb
  );
  $$
);
