#!/usr/bin/env python3
"""Run crawl_html.py for every server-rendered site in data/fingerprint.csv (8 hosts in parallel).

Includes the sites fingerprint.py mislabelled: 'blocked' ones whose only marker was a contact-form captcha,
and 'dead' ones that only failed because Python's TLS stack refuses their old protocol versions (curl works).
"""
import csv, concurrent.futures as cf, os, re, subprocess, sys, urllib.parse

HERE = os.path.dirname(os.path.abspath(__file__))
CURL_OK = {"https://dbt.gov.in", "https://moef.gov.in", "https://mha.gov.in"}  # verified with curl 2026-10-26
FORM_CAPTCHA_ONLY = {"https://www.mib.gov.in", "https://mofpi.gov.in", "https://heavyindustries.gov.in/hi",
                     "https://www.indiapost.gov.in"}  # 'captcha' was a form widget, not a challenge
rows = []
for r in csv.DictReader(open(os.path.join(HERE, "..", "data", "fingerprint.csv"))):
    start = r["final_url"] or r["website"]
    if r["platform"] == "html" or r["website"] in CURL_OK or start in FORM_CAPTCHA_ONLY:
        if start.endswith("/hi") or start.endswith("/hi/"):
            start = re.sub(r"/hi/?$", "/", start)  # crawl the English site
        rows.append((start, r))
jobs = {}
for start, r in rows:
    host = urllib.parse.urlsplit(start).netloc.lower()
    slug = re.sub(r"^www\.|\.gov\.in$|\.nic\.in$", "", host).replace(".", "-")
    jobs.setdefault(slug, (start, "bad-TLS" in r["notes"], []))[2].append(r["name"])
os.makedirs(os.path.join(HERE, "..", "logs"), exist_ok=True)


def run(item):
    slug, (start, insecure, names) = item
    if "--resume" in sys.argv and os.path.exists(os.path.join(HERE, "..", "data", "sites", slug, "pages.csv")):
        return f"{slug}: skipped (done)"
    cmd = [sys.executable, "-I", os.path.join(HERE, "crawl_html.py"), start, slug, "--max-pages", "300"]
    if insecure:
        cmd.append("--insecure")
    log = open(os.path.join(HERE, "..", "logs", f"html_{slug}.log"), "w")
    p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=log, text=True)
    return (p.stdout.strip() or f"{slug}: exit {p.returncode}") + "  <- " + "; ".join(names)


with cf.ThreadPoolExecutor(8) as ex:
    for res in ex.map(run, sorted(jobs.items())):
        print(res, flush=True)
