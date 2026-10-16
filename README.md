# The Nusantara Wire

A daily one-line English digest of Malaysia and Singapore news from the Malay and Chinese-language press, by [@youngsirmuda](https://www.threads.net/@youngsirmuda).

Live: https://mudagogo2021-beep.github.io/nusantara-wire/

## Daily steps
1. **Fetch:** run `./daily.sh`. It writes new items (original-language title, link, source, date) to `runs/YYYY-MM-DD.json`, using the MYT date. `seen.json` makes sure each item comes through only once.
2. **Translate and summarise:** choose up to 15 stories. Write one plain-English line per story, using only facts from the headline and opening paragraph. Do not guess names transliterated from Chinese; describe the person instead (for example, "a businessman"). Save the result as `site/digests/YYYY-MM-DD.json`:
   `{"date":"YYYY-MM-DD","stories":[{"text":"...","source":"...","lang":"ms|zh","link":"..."}]}`
   If there's nothing new, skip the day.
3. **Build and publish:** run `./publish.sh`. It rebuilds `site/index.html`, commits and pushes to `main`, then pushes the `site/` folder to the `gh-pages` branch, which GitHub Pages serves.

## Files
- `sources.json`: feeds and pages. RSS is used for the Malay papers; the Chinese papers and Berita Harian SG are scraped by link pattern.
- `fetch_new.py`: the fetcher. It uses the Python standard library only.
- `build_site.py` and `template.html`: build the static site.
