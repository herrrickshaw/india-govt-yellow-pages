#!/usr/bin/env python3
"""Run extract_postpage.py for every digifootprint-postpage site in data/fingerprint.csv (8 hosts in parallel)."""
import csv, concurrent.futures as cf, os, re, subprocess, sys, urllib.parse

HERE = os.path.dirname(os.path.abspath(__file__))
rows = [r for r in csv.DictReader(open(os.path.join(HERE, "..", "data", "fingerprint.csv")))
        if r["platform"] == "digifootprint-postpage"]
jobs = {}
for r in rows:
    host = urllib.parse.urlsplit(r["api_base"]).netloc
    slug = re.sub(r"^www\.|\.gov\.in$|\.nic\.in$", "", host).replace(".", "-")
    jobs.setdefault(r["api_base"], (slug, []))[1].append(r["name"])
os.makedirs(os.path.join(HERE, "..", "logs"), exist_ok=True)
skip_done = "--resume" in sys.argv


def run(item):
    base, (slug, names) = item
    if skip_done and os.path.exists(os.path.join(HERE, "..", "data", "sites", slug, "summary.json")):
        return slug, "skipped (done)"
    log = open(os.path.join(HERE, "..", "logs", f"{slug}.log"), "w")
    p = subprocess.run([sys.executable, "-I", os.path.join(HERE, "extract_postpage.py"), base, slug],
                       stdout=subprocess.PIPE, stderr=log, text=True)
    return slug, (p.stdout.strip() or f"exit {p.returncode}") + "  <- " + "; ".join(names)


with cf.ThreadPoolExecutor(8) as ex:
    for slug, res in ex.map(run, sorted(jobs.items(), key=lambda kv: kv[1][0])):
        print(res if res.startswith("{") else f"{slug}: {res}", flush=True)
