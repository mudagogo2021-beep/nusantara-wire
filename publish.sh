#!/usr/bin/env bash
# Daily step 3: build site/index.html from site/digests/*.json, commit, push main, and
# publish site/ to the gh-pages branch (GitHub Pages source).
set -euo pipefail
cd "$(dirname "$0")"
python3 build_site.py
git add -A site build_site.py template.html fetch_new.py sources.json daily.sh publish.sh README.md .gitignore
git diff --cached --quiet || git commit -qm "Digest update $(TZ=Asia/Kuala_Lumpur date +%F)"
git push -q origin main
git push -q -f origin "$(git subtree split --prefix site main)":refs/heads/gh-pages
echo "Published: https://mudagogo2021-beep.github.io/nusantara-wire/"
