#!/usr/bin/env python3
"""Ministry of Statistics and Programme Implementation (mospi.gov.in): the site's own JSON API, found in its
JavaScript bundle (2026-10-26). Anonymous POST <base>/<endpoint> with {"page_no","page_size","lang"} returns
{"data":[...], "pagination":{"totalPages"}}; files are file_one/file_two/file_three {"path", "filemime", "filesize"}
relative to https://www.mospi.gov.in/. GET is refused (403); no keys or tokens are used.
Writes data/sites/mospi/{files.csv,documents.jsonl,summary.json}. One request per second.
"""
import csv, json, os, re, time, urllib.request

API, SITE = "https://www.mospi.gov.in/api/", "https://www.mospi.gov.in/"
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0 Safari/537.36"
ENDPOINTS = ["publications-reports/get-web-publications-report-list", "latest-release/get-web-latest-release-list",
             "announcement/get-web-announcement-list", "public-doc/get-web-pub-doc-list", "sdmx-doc/get-web-sdmx-doc-list",
             "tender/get-web-tender-list", "administration/get-web-administration-list",
             "common-doc/get-web-listing-for-dg", "common-doc/get-web-listing-for-ddp", "common-doc/get-web-listing-for-common-web"]
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "sites", "mospi")
os.makedirs(OUT, exist_ok=True)


def post(ep, body):
    time.sleep(1)
    req = urllib.request.Request(API + ep, data=json.dumps(body).encode(), method="POST",
                                 headers={"User-Agent": UA, "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.loads(r.read())
    except Exception as e:
        return {"_error": str(e)[:100]}


def clean(t):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", t or "")).strip()


docs, summary = [], {"api_base": API, "slug": "mospi", "endpoints": {}, "errors": []}
for ep in ENDPOINTS:
    for extra in ({}, {"data_source": "archive"}) if ep.startswith("publications") else ({},):
        page, total, n = 1, 1, 0
        while page <= total:
            d = post(ep, {"page_no": page, "page_size": 100, "lang": "en", **extra})
            if "_error" in d or d.get("status") != "success":
                summary["errors"].append({ep: d.get("_error") or d.get("message"), "page": page, **extra}); break
            for x in d.get("data") or []:
                x["_endpoint"] = ep + (" [archive]" if extra else "")
                docs.append(x); n += 1
            total = int((d.get("pagination") or {}).get("totalPages") or 1)
            page += 1
        summary["endpoints"][ep + (" [archive]" if extra else "")] = n
seen = set()
with open(os.path.join(OUT, "documents.jsonl"), "w") as fj, open(os.path.join(OUT, "files.csv.tmp"), "w", newline="") as fc:
    w = csv.writer(fc)
    w.writerow(["file_id", "title", "file_date", "post_date", "language", "pdf_type", "url", "size", "mime", "hindi_url", "doc_type"])
    for x in docs:
        key = (x["_endpoint"].split(" ")[0], x.get("id"))
        if key in seen:
            continue
        seen.add(key)
        fj.write(json.dumps(x, ensure_ascii=False) + "\n")
        date = x.get("published_year") or x.get("release_date") or x.get("date") or x.get("created_at") or ""
        for slot in ("file_one", "file_two", "file_three", "file", "document"):
            f = x.get(slot)
            if isinstance(f, dict) and f.get("path"):
                w.writerow([f"{x.get('id')}:{slot}", clean(x.get("title") or x.get("name")), date, "", "", "",
                            SITE + f["path"].lstrip("/"), f.get("filesize", ""), f.get("filemime", ""), "", x["_endpoint"]])
        if x.get("file_url"):
            w.writerow([f"{x.get('id')}:file_url", clean(x.get("title")), date, "", "", "", x["file_url"], "", "", "", x["_endpoint"]])
os.replace(os.path.join(OUT, "files.csv.tmp"), os.path.join(OUT, "files.csv"))
summary.update(documents=len(seen), files=sum(1 for _ in open(os.path.join(OUT, "files.csv"))) - 1)
json.dump(summary, open(os.path.join(OUT, "summary.json"), "w"), indent=1)
print(json.dumps(summary, indent=1))
