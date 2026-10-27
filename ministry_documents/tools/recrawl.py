#!/usr/bin/env python3
"""Re-crawl chosen sites without losing earlier results: each site's current doc_links.csv is first merged into
doc_links.prev.csv (build_index.py unions the two), then crawl_html.py runs again, up to 19 hosts in parallel.
Usage: recrawl.py <slug>=<start_url>[:<max_pages>] ...   (insecure TLS taken from fingerprint.csv notes)
"""
import csv, concurrent.futures as cf, os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
D = os.path.join(HERE, "..", "data")
bad_tls = {r["final_url"] or r["website"] for r in csv.DictReader(open(os.path.join(D, "fingerprint.csv")))
           if "bad-TLS" in r["notes"]}


def merge_prev(site):
    links = {}
    for name in ("doc_links.prev.csv", "doc_links.csv"):
        p = os.path.join(site, name)
        if os.path.exists(p):
            for r in csv.DictReader(open(p)):
                links.setdefault(r["url"], r)
    if links:
        with open(os.path.join(site, "doc_links.prev.csv.tmp"), "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=["url", "text", "found_on"], extrasaction="ignore")
            w.writeheader(); w.writerows(links.values())
        os.replace(os.path.join(site, "doc_links.prev.csv.tmp"), os.path.join(site, "doc_links.prev.csv"))


def run(arg):
    slug, rest = arg.split("=", 1)
    start, _, cap = rest.rpartition(":") if rest.rsplit(":", 1)[-1].isdigit() else (rest, "", "300")
    site = os.path.join(D, "sites", slug)
    os.makedirs(site, exist_ok=True)
    merge_prev(site)
    cmd = [sys.executable, "-I", os.path.join(HERE, "crawl_html.py"), start, slug, "--max-pages", cap]
    if start in bad_tls or start.rstrip("/") in bad_tls:
        cmd.append("--insecure")
    with open(os.path.join(HERE, "..", "logs", f"recrawl_{slug}.log"), "w") as log:
        p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=log, text=True)
    return p.stdout.strip() or f"{slug}: exit {p.returncode}"


with cf.ThreadPoolExecutor(19) as ex:
    for res in ex.map(run, sys.argv[1:]):
        print(res, flush=True)
