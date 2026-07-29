#!/bin/bash
until ! pgrep -f "igod_crawl.py" > /dev/null; do sleep 30; done
cd ~/india-govt-yellow-pages
echo "=== crawl done: $(wc -l < data/organizations_index.csv 2>/dev/null) index rows ==="
python3 scripts/igod_org_details.py > data/details.log 2>&1
/usr/bin/python3 scripts/build_db.py 2>&1
echo "=== ALL DONE ==="
