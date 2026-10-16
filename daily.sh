#!/usr/bin/env bash
# Daily step 1: fetch new Malay/Chinese items and write raw JSON for translation.
# Output: runs/YYYY-MM-DD.json (MYT date). Updates seen.json so items appear only once.
set -euo pipefail
cd "$(dirname "$0")"
DAY="${1:-$(TZ=Asia/Kuala_Lumpur date +%F)}"
mkdir -p runs
python3 fetch_new.py --limit-per-source "${LIMIT:-60}" --out "runs/$DAY.json" > /dev/null
echo "runs/$DAY.json: $(python3 -c "import json;print(len(json.load(open('runs/$DAY.json'))))") new items"
