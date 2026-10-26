#!/usr/bin/env python3
"""Merge every site's extraction into one index: data/all_documents.csv (+ DuckDB if available) and data/coverage.csv.

Sources per site folder (data/sites/<slug>/):
  files.csv      API sites (shared CMS, Tribal Affairs): one row per uploaded file, with date/size/language
  documents.jsonl  shared-CMS document groups -> category of each file id
  doc_links.csv  crawled sites: one row per document link with its anchor text and the page it was found on
"""
import csv, glob, json, os, re, subprocess, urllib.parse

HERE = os.path.dirname(os.path.abspath(__file__))
D = os.path.join(HERE, "..", "data")
csv.field_size_limit(10**8)

# slug -> ministry names, platform
names, platform = {}, {}
for r in csv.DictReader(open(os.path.join(D, "fingerprint.csv"))):
    u = r["api_base"] or r["final_url"] or r["website"]
    if not u:
        continue
    host = urllib.parse.urlsplit(u).netloc.lower()
    slug = re.sub(r"^www\.|\.gov\.in$|\.nic\.in$", "", host).replace(".", "-")
    names.setdefault(slug, []).append(r["name"])
    platform.setdefault(slug, r["platform"])
names.setdefault("tribal", ["Tribal Affairs (MoTA)"]); platform["tribal"] = "custom-api"


def ddmmyyyy(s):
    m = re.match(r"(\d{1,2})/(\d{1,2})/(\d{4})", s or "")
    return f"{m.group(3)}-{int(m.group(2)):02d}-{int(m.group(1)):02d}" if m else (s or "")[:10]


rows, cov = [], []
for site in sorted(glob.glob(os.path.join(D, "sites", "*"))):
    slug = os.path.basename(site)
    ministry = "; ".join(names.get(slug, [slug]))
    summ = json.load(open(os.path.join(site, "summary.json"))) if os.path.exists(os.path.join(site, "summary.json")) else {}
    n0 = len(rows)
    cat = {}
    if os.path.exists(os.path.join(site, "documents.jsonl")):
        for line in open(os.path.join(site, "documents.jsonl")):
            d = json.loads(line)
            for f in d.get("files") or []:
                for fid in f.get("file_ids") or []:
                    cat[str(fid)] = (d.get("title") or "", ",".join(d.get("categories") or []) or d.get("type", ""))
    if os.path.exists(os.path.join(site, "files.csv")):
        for r in csv.DictReader(open(os.path.join(site, "files.csv"))):
            grp, c = cat.get(str(r["file_id"]), ("", r.get("doc_type", "")))
            rows.append({"ministry": ministry, "slug": slug, "source": "api", "title": r["title"], "group": grp,
                         "category": c or r.get("division", ""), "date": ddmmyyyy(r["file_date"]) or r["post_date"][:10],
                         "url": r["url"] or r.get("hindi_url", ""), "size": r["size"], "language": r["language"],
                         "found_on": ""})
    # union of the latest crawl and any earlier one kept as doc_links.prev.csv (a re-crawl only adds links)
    links = {}
    for name in ("doc_links.prev.csv", "doc_links.csv"):
        if os.path.exists(os.path.join(site, name)):
            for r in csv.DictReader(open(os.path.join(site, name))):
                links[r["url"]] = r
    if links:
        for r in links.values():
            m = re.search(r"/(20\d{2})[-/](\d{2})/", r["url"])
            rows.append({"ministry": ministry, "slug": slug, "source": "crawl", "title": r["text"], "group": "",
                         "category": "", "date": f"{m.group(1)}-{m.group(2)}" if m else "", "url": r["url"], "size": "",
                         "language": "", "found_on": r["found_on"]})
    cov.append({"slug": slug, "ministry": ministry, "platform": platform.get(slug, ""), "documents": len(rows) - n0,
                "with_url": sum(1 for x in rows[n0:] if x["url"]), "pages_crawled": summ.get("pages", ""),
                "blocked": summ.get("blocked", ""), "errors": len(summ.get("errors", [])) if isinstance(summ.get("errors"), list) else summ.get("errors", "")})

fields = ["ministry", "slug", "source", "title", "group", "category", "date", "url", "size", "language", "found_on"]
with open(os.path.join(D, "all_documents.csv"), "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=fields); w.writeheader(); w.writerows(rows)
with open(os.path.join(D, "coverage.csv"), "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(cov[0])); w.writeheader(); w.writerows(cov)
# DuckDB copy (duckdb lives under /usr/bin/python3 on this Mac)
subprocess.run(["/usr/bin/python3", "-c", f"""
import duckdb; c=duckdb.connect({os.path.join(D, 'ministry_documents.duckdb')!r})
c.execute("create or replace table documents as select * from read_csv_auto({os.path.join(D, 'all_documents.csv')!r}, all_varchar=true)")
c.execute("create or replace table coverage as select * from read_csv_auto({os.path.join(D, 'coverage.csv')!r})")
"""], check=False)
print(len(rows), "documents from", len(cov), "sites")
