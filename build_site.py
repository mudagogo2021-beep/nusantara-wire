#!/usr/bin/env python3
"""Render site/index.html from site/digests/YYYY-MM-DD.json (newest first). Stdlib only."""
import datetime as dt, html, json
from pathlib import Path
SITE = Path(__file__).resolve().parent / "site"
TEMPLATE = (Path(__file__).resolve().parent / "template.html").read_text()
esc = html.escape

def render_day(d):
    day = dt.date.fromisoformat(d["date"])
    items = "\n".join(
        f'<li><p>{esc(s["text"])}</p><a class="src" href="{esc(s["link"])}" target="_blank" rel="noopener">'
        f'<span class="tag {esc(s.get("lang",""))}">{"BM" if s.get("lang")=="ms" else "中文" if s.get("lang")=="zh" else ""}</span>{esc(s["source"])} ↗</a></li>'
        for s in d["stories"])
    return (f'<section class="day" id="{d["date"]}"><header><time datetime="{d["date"]}">{day.strftime("%A, %d %B %Y")}</time>'
            f'<span class="count">{len(d["stories"])} stories</span></header><ol>{items}</ol></section>')

def main():
    days = sorted((json.loads(p.read_text()) for p in (SITE / "digests").glob("*.json")), key=lambda d: d["date"], reverse=True)
    nav = "".join(f'<a href="#{d["date"]}">{dt.date.fromisoformat(d["date"]).strftime("%d %b")}</a>' for d in days[:14])
    out = TEMPLATE.replace("{{NAV}}", nav).replace("{{DAYS}}", "\n".join(map(render_day, days)) or "<p>No digests yet.</p>")
    out = out.replace("{{UPDATED}}", days[0]["date"] if days else "")
    (SITE / "index.html").write_text(out)
    print(f"wrote {SITE/'index.html'} ({len(days)} days)")
if __name__ == "__main__": main()
