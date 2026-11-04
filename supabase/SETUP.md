# הגדרת Supabase ל־מסע הערכים

## 1. יצירת הטבלאות (פעם אחת)
1. בפרויקט ב־Supabase נכנסים ל־**SQL Editor** (בתפריט הצד).
2. לוחצים **New query**.
3. מדביקים את כל התוכן של הקובץ [`schema.sql`](schema.sql) ולוחצים **Run**.
4. אמורה להופיע ההודעה **Success. No rows returned**.

## 2. כתובת האתר (אחרי ש־Netlify נותן כתובת)
1. **Authentication ← URL Configuration**.
2. **Site URL:** כתובת האתר, למשל `https://masa-haarachim.netlify.app`
3. **Redirect URLs ← Add URL:** אותה כתובת, ואחריה `/**`, למשל `https://masa-haarachim.netlify.app/**`
4. שומרים.

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
