# הגדרת Supabase ל־מסע הערכים

## 1. יצירת הטבלאות (פעם אחת)
1. בפרויקט ב־Supabase נכנסים ל־**SQL Editor** (בתפריט הצד).
2. לוחצים **New query**.
3. מדביקים את כל התוכן של הקובץ [`schema.sql`](schema.sql) ולוחצים **Run**.
4. אמורה להופיע ההודעה **Success. No rows returned**.

## 2. כתובת האתר

כתובת האתר הנוכחית: `https://effortless-dieffenbachia-8f7393.netlify.app`

1. **Authentication ← URL Configuration**.
2. **Site URL:** `https://effortless-dieffenbachia-8f7393.netlify.app`
3. **Redirect URLs ← Add URL:** `https://effortless-dieffenbachia-8f7393.netlify.app/**`
4. אם משנים את שם האתר ב־Netlify, צריך לעדכן גם כאן.
5. שומרים.

בלי השלב הזה, הלינק שמגיע במייל לא יחזיר את המתאמן לאפליקציה.

## 3. מייל הכניסה בעברית (לא חובה)
**Authentication ← Emails ← Magic Link**: מחליפים את הנושא והתוכן.

נושא:
```
הכניסה שלך למסע הערכים
```
תוכן:
```html
<div dir="rtl" style="font-family:Arial,sans-serif">
  <h2>מסע הערכים</h2>
  <p>לחיצה על הכפתור מכניסה למסע. אין צורך בסיסמה.</p>
  <p><a href="{{ .ConfirmationURL }}">כניסה למסע</a></p>
  <p style="color:#7A7067">אם לא ביקשת להיכנס, אפשר להתעלם מהמייל.</p>
</div>
```

## מגבלה של התוכנית החינמית
שירות המייל המובנה של Supabase שולח רק מעט מיילים בשעה. זה מספיק לבדיקות ולפיילוט קטן. לפני שמזמינים הרבה מתאמנים, מחברים שירות מייל חינמי כמו Brevo (**Authentication ← Emails ← SMTP Settings**).

## מה לא משתפים
- את **סיסמת המסד**.
- את המפתח **secret** או **service_role**.

המפתח **publishable** והכתובת של הפרויקט נמצאים בתוך האפליקציה. זה תקין, כי ההרשאות בטבלאות (RLS) מאפשרות לכל משתמש לראות רק את הנתונים של עצמו.

---

# שלב 4: תזכורות לאתגר השבועי

את הקודים הסודיים (VAPID_PRIVATE_KEY ו־CRON_SECRET) קיבלת בשיחה. **הם לא שמורים ב־repo**, ולא משתפים אותם עם אף אחד.

## 1. טבלאות התזכורות
**SQL Editor ← New query** ← מדביקים את כל התוכן של [`schema-reminders.sql`](schema-reminders.sql) ← **Run**.

## 2. הקודים הסודיים של הפונקציה
**Edge Functions ← Secrets** (או **Project Settings ← Edge Functions**). מוסיפים ארבעה קודים:

| Name | Value |
|---|---|
| `VAPID_PUBLIC_KEY` | `BPR3MR8W-4bWRCetm4occkaJxEhA7UmHb257v1TdWRUC37jhcwXeN9yUNAVWINEBh4dVGCRIHKt8DDzbuLhNcs0` |
| `VAPID_PRIVATE_KEY` | הקוד הסודי מהשיחה |
| `CRON_SECRET` | הקוד הסודי מהשיחה |
| `SITE_URL` | `https://effortless-dieffenbachia-8f7393.netlify.app` |

## 3. פרסום הפונקציה
1. **Edge Functions ← Deploy a new function ← Via Editor**.
2. שם הפונקציה: `send-reminders` (בדיוק כך).
3. מוחקים את הקוד לדוגמה ומדביקים את כל התוכן של [`functions/send-reminders/index.ts`](functions/send-reminders/index.ts).
4. לוחצים **Deploy**.
5. בהגדרות הפונקציה מכבים את **Verify JWT** (או **Enforce JWT verification**) ושומרים.

## 4. הפעלת התזמון
**SQL Editor ← New query** ← מדביקים את [`schedule-reminders.sql`](schedule-reminders.sql), מחליפים את `PASTE_CRON_SECRET_HERE` בקוד ה־CRON_SECRET ← **Run**.

## 5. בדיקה
1. באפליקציה: נכנסים עם מייל, משלימים תחנה אחת, ופותחים את מסך **אתגר**.
2. מפעילים **התראה בטלפון** ומאשרים. באייפון צריך קודם להוסיף את האתר למסך הבית ולפתוח אותו משם.
3. לוחצים **לקבל התראה לדוגמה עכשיו**. אמורה להגיע התראה אמיתית לטלפון.
4. כדי לבדוק את התזמון: בוחרים את היום של היום ושעה שעברה כבר. תוך 15 דקות אמורה להגיע התראת "האתגר השבועי שלך".
