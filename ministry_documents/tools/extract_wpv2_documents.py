#!/usr/bin/env python3
"""Shared-CMS sites that have no documents_category taxonomy and an empty central_documents registry
(e.g. rural.gov.in, 2026-10-26): read the standard WordPress route /wp/v2/documents (acf.file[].pdf = media id)
and resolve each media id with /wp/v2/media?include=... (batches of 50). Writes files.csv + documents.jsonl
in the same shape as extract_postpage.py. One request per second. Usage: extract_wpv2_documents.py <api_base> <slug>
"""
import csv, json, os, sys, time, urllib.request

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0 Safari/537.36"
base, slug = sys.argv[1].rstrip("/"), sys.argv[2]
out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "sites", slug)
os.makedirs(out, exist_ok=True)


def get(path):
    time.sleep(1)
    with urllib.request.urlopen(urllib.request.Request(f"{base}/{path}", headers={"User-Agent": UA}), timeout=60) as r:
        return json.loads(r.read()), r.headers


docs, page = [], 1
while True:
    d, h = get(f"wp/v2/documents?per_page=100&page={page}&_fields=id,date,modified,slug,title,acf")
    docs += d
    if page >= int(h.get("X-WP-TotalPages") or 1):
        break
    page += 1
ids = []
for d in docs:
    for f in (d.get("acf") or {}).get("file") or []:
        if isinstance(f, dict) and isinstance(f.get("pdf"), int):
            ids.append(f["pdf"])
media = {}
for i in range(0, len(ids), 50):
    for m in get("wp/v2/media?per_page=50&include=" + ",".join(map(str, ids[i:i + 50])) + "&_fields=id,source_url,mime_type,media_details")[0]:
        media[m["id"]] = m
with open(os.path.join(out, "documents.jsonl"), "w") as fj, open(os.path.join(out, "files.csv.tmp"), "w", newline="") as fc:
    w = csv.writer(fc)
    w.writerow(["file_id", "title", "file_date", "post_date", "language", "pdf_type", "url", "size", "mime", "hindi_url"])
    for d in docs:
        a = d.get("acf") or {}
        files = []
        for f in a.get("file") or []:
            if not isinstance(f, dict):
                continue
            m = media.get(f.get("pdf"), {})
            files.append({"type": "PDF", "title": f.get("title"), "external_link": "", "file_ids": [f.get("pdf")]})
            w.writerow([f.get("pdf"), (f.get("title") or a.get("title") or "").strip(), f.get("file_date") or a.get("date") or "",
                        d.get("date", ""), ",".join(f.get("language") or []), "", m.get("source_url", ""),
                        (m.get("media_details") or {}).get("filesize", ""), m.get("mime_type", ""), ""])
        fj.write(json.dumps({"id": d["id"], "title": (a.get("title") or (d.get("title") or {}).get("rendered") or "").strip(),
                             "date": a.get("date", ""), "post_date": d.get("date"), "modified": d.get("modified"), "slug": d.get("slug"),
                             "categories": [a.get("select_documents_type") or ""], "files": files}, ensure_ascii=False) + "\n")
os.replace(os.path.join(out, "files.csv.tmp"), os.path.join(out, "files.csv"))
json.dump({"api_base": base, "slug": slug, "method": "wp/v2/documents + wp/v2/media", "documents": len(docs),
           "files": len(ids), "resolved": sum(1 for i in ids if i in media), "errors": []},
          open(os.path.join(out, "summary.json"), "w"), indent=1)
print(json.dumps({"slug": slug, "documents": len(docs), "files": len(ids), "resolved": sum(1 for i in ids if i in media)}))
