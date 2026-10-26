#!/usr/bin/env python3
"""Ministry of Tribal Affairs (tribal.gov.in): custom JSON API found by capturing the site's own calls (2026-10-26).
GET /api/v1/documents?pageSize=100&page=N -> {"items", "total", "totalPages"}; file.url is relative to the site.
Writes data/sites/tribal/{files.csv,documents.jsonl,summary.json}. One request per second, read-only.
"""
import csv, json, os, time, urllib.request

BASE = "https://tribal.gov.in"
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0 Safari/537.36"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "sites", "tribal")
os.makedirs(OUT, exist_ok=True)


def get(path):
    time.sleep(1)
    req = urllib.request.Request(BASE + path, headers={"User-Agent": UA, "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read())


page, total, items = 1, 1, []
while page <= total:
    d = get(f"/api/v1/documents?pageSize=100&page={page}")
    items += d["items"]
    total = d["totalPages"]
    page += 1
with open(os.path.join(OUT, "documents.jsonl"), "w") as f:
    for x in items:
        f.write(json.dumps(x, ensure_ascii=False) + "\n")
with open(os.path.join(OUT, "files.csv"), "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["file_id", "title", "file_date", "post_date", "language", "pdf_type", "url", "size", "mime", "hindi_url",
                "doc_type", "division", "financial_year"])
    for x in items:
        fl = x.get("file") or {}
        url = (BASE + fl["url"]) if fl.get("url", "").startswith("/") else (fl.get("url") or x.get("externalUrl") or "")
        w.writerow([x["id"], (x.get("title") or {}).get("en", ""), x.get("documentDate", ""), x.get("publishedAt", ""),
                    x.get("language") or "", "", url, int((fl.get("sizeKb") or 0) * 1024) or "", fl.get("mimeType", ""), "",
                    x.get("type", ""), x.get("division", ""), x.get("financialYear", "")])
json.dump({"api_base": BASE + "/api/v1", "slug": "tribal", "files": len(items), "documents": len(items)},
          open(os.path.join(OUT, "summary.json"), "w"), indent=1)
print(len(items), "documents")
