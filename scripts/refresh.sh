#!/bin/bash
# Monthly refresh of the India government yellow pages.
# Re-crawls igod.gov.in, re-extracts contacts/who's-who, re-links policies,
# rebuilds DuckDB, commits and pushes.
set -uo pipefail
REPO="$HOME/india-govt-yellow-pages"
LOG="$REPO/logs/refresh-$(date +%Y-%m-%d).log"
mkdir -p "$REPO/logs"
exec >> "$LOG" 2>&1
echo "=== refresh started $(date) ==="
cd "$REPO" || exit 1

python3 scripts/igod_crawl.py || { echo "crawl FAILED"; exit 1; }
python3 scripts/igod_org_details.py || { echo "details FAILED"; exit 1; }
python3 scripts/link_policy_contacts.py || echo "linkage FAILED (continuing)"
/usr/bin/python3 scripts/build_db.py || echo "duckdb build FAILED (continuing)"
python3 scripts/build_dashboard.py || echo "dashboard build FAILED (continuing)"

git add data/ dashboard/ && git commit -m "chore: monthly refresh $(date +%Y-%m-%d)" \
  && git push origin main
echo "=== refresh finished $(date) ==="
