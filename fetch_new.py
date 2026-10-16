#!/usr/bin/env python3
"""Fetch new Malay/Chinese news items for the @youngsirmuda daily digest.

Usage: python3 fetch_new.py [--limit-per-source N] [--dry-run] [--out FILE]
Prints a JSON array of NEW items (not in seen.json): title (original language),
link, source, source_id, lang, country, date. Standard library only.
Seen-list: seen.json (link -> first-seen ISO time), pruned after 30 days.
"""
import argparse, datetime as dt, email.utils, html, json, re, sys, urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.parse import urljoin, urldefrag

HERE = Path(__file__).resolve().parent
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36"
NOW = dt.datetime.now(dt.timezone.utc)

def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "ms,zh;q=0.9,en;q=0.5"})
    with urllib.request.urlopen(req, timeout=25) as r:
        return r.read().decode(r.headers.get_content_charset() or "utf-8", "replace")

def clean(s):
    s = html.unescape(re.sub(r"<[^>]+>", " ", s or ""))
    return re.sub(r"\s+", " ", s).strip()

def norm_link(u):
    u = urldefrag(u.strip())[0]
    return u.split("?")[0] if "orientaldaily" in u or "sinchew" in u else u

def parse_rss(src, text):
    root = ET.fromstring(text.encode("utf-8"))
    out = []
    for it in root.iter("item"):
        t, l = clean(it.findtext("title")), (it.findtext("link") or "").strip()
        d = it.findtext("pubDate")
        try: d = email.utils.parsedate_to_datetime(d).isoformat() if d else None
        except Exception: d = None
        if t and l: out.append({"title": t, "link": norm_link(l), "date": d})
    return out

def date_from_url(link):
    m = re.search(r"(20\d{2})/?(\d{2})/?(\d{2})", link)
    return f"{m.group(1)}-{m.group(2)}-{m.group(3)}" if m else None

def parse_html(src, text):
    pat, base, best = re.compile(src["pattern"]), src.get("base", src["url"]), {}
    for attrs, inner in re.findall(r'<a\b([^>]*)>(.*?)</a>', text, re.S):
        h = re.search(r'href="([^"]+)"', attrs)
        if not h: continue
        link = norm_link(urljoin(base, html.unescape(h.group(1))))
        if not pat.match(link): continue
        ta = re.search(r'title="([^"]+)"', attrs)
        title = clean(inner)
        if ta and len(clean(ta.group(1))) > len(title): title = clean(ta.group(1))
        if len(title) < 6 or len(title.split()) < src.get("min_title_words", 0): continue
        if len(title) > len(best.get(link, "")): best[link] = title
    return [{"title": t, "link": l, "date": date_from_url(l)} for l, t in best.items()]

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit-per-source", type=int, default=25)
    ap.add_argument("--dry-run", action="store_true", help="don't update seen.json")
    ap.add_argument("--out", help="also write JSON to this file")
    ap.add_argument("--seen", default=str(HERE / "seen.json"))
    a = ap.parse_args()
    sources = json.loads((HERE / "sources.json").read_text())
    seen_p = Path(a.seen)
    seen = json.loads(seen_p.read_text()) if seen_p.exists() else {}
    cutoff = (NOW - dt.timedelta(days=30)).isoformat()
    seen = {k: v for k, v in seen.items() if v >= cutoff}
    new, status = [], {}
    for s in sources:
        try:
            text = get(s["url"])
            items = parse_rss(s, text) if s["type"] == "rss" else parse_html(s, text)
            status[s["id"]] = f"ok ({len(items)} found)"
        except Exception as e:
            status[s["id"]] = f"error: {e.__class__.__name__}: {e}"; continue
        n = 0
        for it in items:
            if it["link"] in seen or n >= a.limit_per_source: continue
            seen[it["link"]] = NOW.isoformat(); n += 1
            new.append({"title": it["title"], "link": it["link"], "source": s["name"], "source_id": s["id"],
                        "lang": s["lang"], "country": s["country"], "date": it["date"] or NOW.date().isoformat()})
    print(json.dumps(status, ensure_ascii=False), file=sys.stderr)
    out = json.dumps(new, ensure_ascii=False, indent=1)
    if a.out: Path(a.out).write_text(out)
    print(out)
    if not a.dry_run:
        seen_p.write_text(json.dumps(seen, ensure_ascii=False))

if __name__ == "__main__":
    main()
