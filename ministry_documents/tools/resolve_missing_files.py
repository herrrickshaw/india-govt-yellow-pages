#!/usr/bin/env python3
"""For shared-CMS sites whose document entries reference file ids missing from the bulk central_documents
registry, resolve each id with post-page/post?id=<id> (the call the sites' own pages make) and append it to
files.csv. One request per second per host; sites in parallel. Usage: resolve_missing_files.py <slug> [...]
"""
import csv, concurrent.futures as cf, json, os, sys, time, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0 Safari/537.36"
CAP = 3000


def resolve(slug):
    d = os.path.join(HERE, "..", "data", "sites", slug)
    base = json.load(open(os.path.join(d, "summary.json")))["api_base"]
    have = {r["file_id"] for r in csv.DictReader(open(os.path.join(d, "files.csv")))}
    want = []
    for line in open(os.path.join(d, "documents.jsonl")):
        for f in json.loads(line).get("files") or []:
            want += [str(i) for i in f.get("file_ids") or [] if str(i) not in have]
    want = list(dict.fromkeys(want))[:CAP]
    added = 0
    with open(os.path.join(d, "files.csv"), "a", newline="") as fh:
        w = csv.writer(fh)
        for fid in want:
            time.sleep(1)
            try:
                req = urllib.request.Request(f"{base}/post-page/post?id={fid}", headers={"User-Agent": UA})
                p = json.loads(urllib.request.urlopen(req, timeout=60).read()).get("posts") or {}
            except Exception:
                continue
            a = p.get("acf_data") or {}
            pdf = a.get("pdf") if isinstance(a.get("pdf"), dict) else {}
            if not pdf.get("url") and isinstance(a.get("file"), dict):
                pdf = a["file"]
            w.writerow([fid, (a.get("title") or p.get("post_title") or "").strip(), a.get("file_date", ""), p.get("post_date", ""),
                        ",".join(a["language"]) if isinstance(a.get("language"), list) else a.get("language", ""),
                        a.get("pdf_type", ""), pdf.get("url", ""), pdf.get("filesize", ""), pdf.get("mime_type", ""), ""])
            added += 1
    return f"{slug}: {len(want)} missing ids, {added} resolved"


with cf.ThreadPoolExecutor(8) as ex:
    for r in ex.map(resolve, sys.argv[1:]):
        print(r, flush=True)
