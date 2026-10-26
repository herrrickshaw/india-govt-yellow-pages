#!/usr/bin/env python3
"""Retry the bulk central_documents pages that failed (HTTP 500) in a site's extraction.

A 100-record page that 500s usually holds one bad record, so each failed page p is re-requested as ten
10-record pages covering the same range (limit=10, pages (p-1)*10+1 .. p*10), then 1-record pages inside any
10-record page that still fails. Recovered rows are appended to files.csv (deduplicated by file_id) and the
summary's error list is rewritten with what is still missing. One request per second, backoff on 5xx.
Usage: retry_bulk_pages.py <slug> [<slug> ...]
"""
import csv, json, os, sys, time, urllib.request, http.cookiejar

HERE = os.path.dirname(os.path.abspath(__file__))
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0 Safari/537.36"
op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))
last = [0.0]


def get(url, tries=3):
    for a in range(tries):
        time.sleep(max(0, 1.0 - (time.time() - last[0]))); last[0] = time.time()
        try:
            with op.open(urllib.request.Request(url, headers={"User-Agent": UA}), timeout=45) as r:
                return json.loads(r.read())
        except urllib.error.HTTPError as e:
            if e.code >= 500 and a < tries - 1:
                time.sleep(5 * (a + 1)); continue
            return None
        except Exception:
            if a < tries - 1:
                time.sleep(5 * (a + 1)); continue
            return None


def row(p):
    a = p.get("acf_data") or {}
    withurl = [v for v in a.values() if isinstance(v, dict) and v.get("url")]
    pdf = withurl[0] if withurl else {}
    hin = withurl[1] if len(withurl) > 1 else {}
    lang = ",".join(a["language"]) if isinstance(a.get("language"), list) else a.get("language", "")
    return [p.get("ID"), (a.get("title") or p.get("post_title") or "").strip(), a.get("file_date", ""), p.get("post_date", ""),
            lang, a.get("pdf_type", ""), pdf.get("url", ""), pdf.get("filesize", ""), pdf.get("mime_type", ""), hin.get("url", "")]


def retry(slug):
    d = os.path.join(HERE, "..", "data", "sites", slug)
    summ = json.load(open(os.path.join(d, "summary.json")))
    base = summ["api_base"]
    failed = sorted({e["central_documents"]["_page"] for e in summ.get("errors", []) if "central_documents" in e})
    have = {r["file_id"] for r in csv.DictReader(open(os.path.join(d, "files.csv")))}
    got, still = [], []
    for p in failed:
        for q in range((p - 1) * 10 + 1, p * 10 + 1):
            j = get(f"{base}/post-page/central_documents?limit=10&page={q}")
            if j is not None:
                got += j.get("posts") or []
                continue
            for k in range((q - 1) * 10 + 1, q * 10 + 1):  # isolate the bad record(s)
                j1 = get(f"{base}/post-page/central_documents?limit=1&page={k}", tries=2)
                if j1 is None:
                    still.append(k)
                else:
                    got += j1.get("posts") or []
    new = [row(p) for p in got if str(p.get("ID")) not in have]
    with open(os.path.join(d, "files.csv"), "a", newline="") as f:
        csv.writer(f).writerows(new)
    summ["errors"] = [e for e in summ.get("errors", []) if "central_documents" not in e]
    if still:
        summ["errors"].append({"central_documents_unrecoverable_records(limit=1 pages)": still})
    summ["files"] = len(have) + len(new)
    summ["retried"] = time.strftime("%Y-%m-%dT%H:%M:%S")
    json.dump(summ, open(os.path.join(d, "summary.json"), "w"), indent=1)
    return f"{slug}: {len(failed)} failed pages -> recovered {len(new)} records; {len(still)} single records still failing"


for s in sys.argv[1:]:
    print(retry(s), flush=True)
