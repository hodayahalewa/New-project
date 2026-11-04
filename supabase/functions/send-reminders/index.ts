// מסע הערכים: שליחת תזכורות לאתגר השבועי (Supabase Edge Function)
//
// Two ways in:
//  1. The scheduler (pg_cron, every 15 minutes) calls with header x-cron-secret. The function sends
//     the weekly challenge to everyone whose day and time arrived, and a gentle nudge 3 days later
//     to anyone who has not marked the challenge as done.
//  2. A signed-in user calls with { test: true } to get a test notification on their own devices.
//
// Secrets to set in Supabase (Edge Functions → Secrets): VAPID_PUBLIC_KEY, VAPID_PRIVATE_KEY,
// CRON_SECRET, SITE_URL. SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY are provided automatically.
// Deploy with "Verify JWT" turned off: the scheduler has no user token; test calls are checked below.

import { createClient } from "npm:@supabase/supabase-js@2.118.0";
import webpush from "npm:web-push@3.6.7";

const admin = createClient(Deno.env.get("SUPABASE_URL")!, Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!);
const SITE_URL = Deno.env.get("SITE_URL") ?? "https://example.com";
webpush.setVapidDetails(SITE_URL, Deno.env.get("VAPID_PUBLIC_KEY")!, Deno.env.get("VAPID_PRIVATE_KEY")!);

const cors = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers": "authorization, x-client-info, apikey, content-type",
};
const json = (body: unknown, status = 200) =>
  new Response(JSON.stringify(body), { status, headers: { ...cors, "Content-Type": "application/json" } });

const DOW = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];
function localNow(tz: string) {
  const parts = Object.fromEntries(
    new Intl.DateTimeFormat("en-US", {
      timeZone: tz, weekday: "short", year: "numeric", month: "2-digit", day: "2-digit",
      hour: "2-digit", minute: "2-digit", hourCycle: "h23",
    }).formatToParts(new Date()).map((p) => [p.type, p.value]),
  );
  return { dow: DOW.indexOf(parts.weekday), date: `${parts.year}-${parts.month}-${parts.day}`, hm: `${parts.hour}:${parts.minute}` };
}
const daysBetween = (a: string, b: string) => Math.round((Date.parse(b) - Date.parse(a)) / 86400000);

async function sendTo(userId: string, payload: Record<string, string>) {
  const { data: subs } = await admin.from("push_subscriptions").select("endpoint,p256dh,auth").eq("user_id", userId);
  let sent = 0;
  for (const s of subs ?? []) {
    try {
      await webpush.sendNotification({ endpoint: s.endpoint, keys: { p256dh: s.p256dh, auth: s.auth } }, JSON.stringify(payload), { TTL: 86400 });
      sent++;
    } catch (e) {
      const code = (e as { statusCode?: number }).statusCode;
      if (code === 404 || code === 410) await admin.from("push_subscriptions").delete().eq("endpoint", s.endpoint);
      else console.error("push failed", code, (e as Error).message);
    }
  }
  return sent;
}

Deno.serve(async (req) => {
  if (req.method === "OPTIONS") return new Response("ok", { headers: cors });
  const body = await req.json().catch(() => ({}));

  // Test notification for the signed-in user
  if (body.test) {
    const token = (req.headers.get("Authorization") ?? "").replace(/^Bearer\s+/i, "");
    const { data: { user } } = await admin.auth.getUser(token);
    if (!user) return json({ error: "not signed in" }, 401);
    const { data: p } = await admin.from("profiles").select("next_challenge,next_challenge_value").eq("id", user.id).maybeSingle();
    const sent = await sendTo(user.id, {
      title: "מסע הערכים",
      body: p?.next_challenge ? `האתגר השבועי (${p.next_challenge_value}): ${p.next_challenge}` : "ההתראות פועלות. האתגר הראשון יגיע אחרי התחנה הראשונה.",
      url: "./?go=challenge",
      tag: "masa-test",
    });
    return json({ sent });
  }

  // Scheduled run
  if (req.headers.get("x-cron-secret") !== Deno.env.get("CRON_SECRET")) return json({ error: "unauthorized" }, 401);
  const { data: profiles, error } = await admin.from("profiles")
    .select("id,tz,reminder_day,reminder_time,next_challenge,next_challenge_value,challenges_done,last_sent_on,last_sent_challenges,nudged_for")
    .eq("push_enabled", true).not("next_challenge", "is", null);
  if (error) return json({ error: error.message }, 500);

  let weekly = 0, nudges = 0;
  for (const p of profiles ?? []) {
    const now = localNow(p.tz || "Asia/Jerusalem");
    const time = p.reminder_time || "09:00";
    if (p.reminder_day === now.dow && now.hm >= time && p.last_sent_on !== now.date) {
      const sent = await sendTo(p.id, { title: "האתגר השבועי שלך", body: `${p.next_challenge_value}: ${p.next_challenge}`, url: "./?go=challenge" });
      if (sent) {
        await admin.from("profiles").update({ last_sent_on: now.date, last_sent_challenges: p.challenges_done ?? 0, nudged_for: null }).eq("id", p.id);
        weekly++;
      }
    } else if (
      p.last_sent_on && p.nudged_for !== p.last_sent_on && daysBetween(p.last_sent_on, now.date) >= 3 &&
      (p.challenges_done ?? 0) <= (p.last_sent_challenges ?? 0) && now.hm >= time
    ) {
      const sent = await sendTo(p.id, { title: "תזכורת עדינה", body: `האתגר של השבוע עוד מחכה: ${p.next_challenge}`, url: "./?go=challenge", tag: "masa-nudge" });
      if (sent) {
        await admin.from("profiles").update({ nudged_for: p.last_sent_on }).eq("id", p.id);
        nudges++;
      }
    }
  }
  return json({ checked: profiles?.length ?? 0, weekly, nudges });
});
