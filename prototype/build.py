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
    (OUT / "index.html").write_text(html, encoding="utf-8")
    print(f"values={len(values)} domains={len(domains)} "
          f"questions={sum(len(d['s1']) + len(d['s2']) + len(d['s3']) for d in domains)} "
          f"size={len(html) // 1024}KB")


if __name__ == "__main__":
    main()
