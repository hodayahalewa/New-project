"""Build the clickable prototype from the approved content.

Reads docs/values.md and docs/pools/*.md, embeds them as JSON plus the logo
images, and writes prototype/index.html from prototype/template.html.
Run: python3 prototype/build.py
"""
import base64
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Supabase project. The publishable key is meant to ship inside the app; access is limited by
# row-level security (see supabase/schema.sql). Never put the secret / service_role key here.
SUPABASE = {"url": "https://jilxleducctilebsvtlp.supabase.co", "key": "sb_publishable__4oLgDJ2EcgQIrXKABLs9w_HZtZJCs6"}
SUPABASE_JS = "vendor/supabase-2.118.0.js"
# Web Push public key (the private half lives only in Supabase Edge Function secrets).
VAPID_PUBLIC = "BPR3MR8W-4bWRCetm4occkaJxEhA7UmHb257v1TdWRUC37jhcwXeN9yUNAVWINEBh4dVGCRIHKt8DDzbuLhNcs0"
DOCS = ROOT / "docs"
OUT = ROOT / "prototype"

DOMAINS = [
    ("family", "משפחה", "כפר השורשים", "🏡", ""),
    ("relationship", "זוגיות", "גשר הלבבות", "💞", "אפשר לענות על הזוגיות של היום, או על הזוגיות שהיית רוצה."),
    ("career", "קריירה ועבודה", "עיר המגדלים", "💼", ""),
    ("friends", "חברים", "כיכר המפגשים", "🤝", ""),
    ("self-growth", "מימוש עצמי וצמיחה", "הר הפסגה", "🌱", ""),
    ("health", "בריאות וגוף", "מעיין החיוניות", "🌿", ""),
    ("money", "כסף ושפע", "עמק השפע", "💰", ""),
    ("leisure", "פנאי והנאה", "חוף השמחה", "🎈", ""),
]


def parse_values():
    values, family = [], None
    for line in (DOCS / "values.md").read_text(encoding="utf-8").splitlines():
        h = re.match(r"^## (\S+) (.+?)( 🆕)?$", line)
        if h:
            family = h.group(2).strip()
            continue
        m = re.match(r"^\| (\S+) \| (.+?) \| (.+?) \| (.+?) \| (.+?) \|$", line)
        if not m or m.group(2) in ("ערך",) or set(m.group(1)) <= set("-"):
            continue
        name = m.group(2).replace("🆕", "").strip()
        values.append({
            "icon": m.group(1), "name": name, "family": family,
            "desc": m.group(3).strip(), "reflect": m.group(4).strip(), "challenge": m.group(5).strip(),
        })
    return values


def tags(s):
    return [t.strip() for t in s.split(",") if t.strip()]


def parse_pool(path):
    stage, pool = 0, {"s1": [], "s2": [], "s3": []}
    cur = None
    for line in path.read_text(encoding="utf-8").splitlines():
        st = re.match(r"^## שלב (\d)", line)
        if st:
            stage = int(st.group(1))
            continue
        if stage == 1:
            m = re.match(r"^\| \d+ \| (.+?) \*\((.+?)\)\* \| (.+?) \*\((.+?)\)\* \|$", line)
            if m:
                pool["s1"].append({"a": m.group(1).strip(), "av": tags(m.group(2)),
                                   "b": m.group(3).strip(), "bv": tags(m.group(4))})
        elif stage in (2, 3):
            q = re.match(r"^\*\*\d+\. (.+?)\*\*$", line)
            if q:
                cur = {"q": q.group(1).strip(), "opts": []}
                pool[f"s{stage}"].append(cur)
                continue
            o = re.match(r"^- [א-ד]\. (.+?) \*\((.+?)\)\*$", line)
            if o and cur is not None:
                cur["opts"].append({"t": o.group(1).strip(), "v": tags(o.group(2))})
                continue
            t = re.match(r"^> ההתנגשות: (.+)$", line)
            if t and cur is not None:
                cur["tension"] = t.group(1).strip()
    return pool


def data_uri(path, mime):
    return f"data:{mime};base64," + base64.b64encode(path.read_bytes()).decode()


def main():
    values = parse_values()
    names = {v["name"] for v in values}
    domains = []
    for key, name, place, icon, intro in DOMAINS:
        pool = parse_pool(DOCS / "pools" / f"{key}.md")
        for q in pool["s1"]:
            assert set(q["av"] + q["bv"]) <= names, (key, q)
        for st in ("s2", "s3"):
            for q in pool[st]:
                for o in q["opts"]:
                    assert set(o["v"]) <= names, (key, o)
        assert len(pool["s1"]) >= 5 and len(pool["s2"]) >= 4 and len(pool["s3"]) >= 2, key
        domains.append({"id": key, "name": name, "place": place, "icon": icon, "intro": intro, **pool})
    data = {"values": values, "domains": domains}
    html = (OUT / "template.html").read_text(encoding="utf-8")
    html = html.replace("__DATA__", json.dumps(data, ensure_ascii=False))
    html = html.replace("__LEAF__", data_uri(DOCS / "design/img/leaf-cutout.png", "image/png"))
    html = html.replace("__SPROUT__", data_uri(DOCS / "design/img/sprout-cutout.png", "image/png"))
    html = html.replace("__PATHIMG__", data_uri(DOCS / "design/img/path.jpg", "image/jpeg"))
    # Artifact preview: works offline, no cloud.
    (OUT / "index.html").write_text(html.replace("__SUPABASE_SCRIPT__", "").replace("__CLOUD__", "null").replace("__VAPID__", "null"), encoding="utf-8")
    # Hosted site: real login and cloud save.
    html = html.replace("__SUPABASE_SCRIPT__", f'<script src="{SUPABASE_JS}"></script>\n').replace("__CLOUD__", json.dumps(SUPABASE)).replace("__VAPID__", json.dumps(VAPID_PUBLIC))
    # Standalone copy for hosting (Netlify): same page wrapped in a full HTML document.
    site = ROOT / "site"
    site.mkdir(exist_ok=True)
    head = ('<!doctype html>\n<html lang="he" dir="rtl">\n<head>\n<meta charset="utf-8">\n'
            '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
            '<meta name="theme-color" content="#FAF6F0">\n<meta name="color-scheme" content="only light">\n'
            '<link rel="manifest" href="manifest.webmanifest">\n'
            '<link rel="apple-touch-icon" href="icons/apple-touch-icon.png">\n'
            '<link rel="icon" type="image/png" sizes="192x192" href="icons/icon-192.png">\n'
            '<meta name="apple-mobile-web-app-capable" content="yes">\n'
            '<meta name="apple-mobile-web-app-title" content="מסע הערכים">\n')
    title_end = html.index("</title>") + len("</title>")
    page = head + html[:title_end] + "\n" + html[title_end:].split("<div class=\"app\"", 1)[0] \
        + "</head>\n<body>\n<div class=\"app\"" + html[title_end:].split("<div class=\"app\"", 1)[1] + "\n</body>\n</html>\n"
    (site / "index.html").write_text(page, encoding="utf-8")
    print(f"values={len(values)} domains={len(domains)} "
          f"questions={sum(len(d['s1']) + len(d['s2']) + len(d['s3']) for d in domains)} "
          f"size={len(html) // 1024}KB")


if __name__ == "__main__":
    main()
