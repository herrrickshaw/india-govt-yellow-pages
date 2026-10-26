#!/usr/bin/env python3
"""Fallback crawler for JavaScript-only ministry sites: render pages with Obscura and collect document links.

Renders the start page, then same-site links whose URL or text looks document-related, depth <= 2,
max N renders. Uses the standard Obscura build (no stealth); stops on a host that serves a bot challenge.
Usage: crawl_js.py <start_url> <slug> [--max-pages 40]
Writes data/sites/<slug>/{doc_links.csv,pages.csv,summary.json} (same shape as crawl_html.py).
"""
import csv, json, os, re, subprocess, sys, time, urllib.parse
from collections import deque

OBSCURA = os.path.expanduser("~/.local/share/obscura/obscura")
HERE = os.path.dirname(os.path.abspath(__file__))
DOC = re.compile(r"\.(pdf|docx?|xlsx?|csv|zip|pptx?)(?:$|[?#])", re.I)
HINT = re.compile(r"(?i)document|report|publication|notification|circular|order|notice|guideline|scheme|policy|"
                  r"act|rule|statistic|annual|budget|press|tender|gazette|archive|whats-?new|minutes|monthly|division")
CHALLENGE = re.compile(r"(?is)just a moment\.\.\.|challenge-platform|cf-chl-|client challenge|verify (?:that )?you(?:'| a)re")


def render_links(url):
    p = subprocess.run([OBSCURA, "fetch", url, "--wait", "6", "--timeout", "40", "--dump", "links"],
                       capture_output=True, text=True, timeout=120)
    links = []
    for line in p.stdout.splitlines():
        if line.startswith(("Fetching ", "Page loaded")):
            continue
        u, _, t = line.partition("\t")
        if u.startswith("http"):
            links.append((u.strip(), t.strip()[:300]))
    return links, p.stdout


def main():
    start, slug = sys.argv[1], sys.argv[2]
    maxp = int(sys.argv[sys.argv.index("--max-pages") + 1]) if "--max-pages" in sys.argv else 40
    out = os.path.join(HERE, "..", "data", "sites", slug)
    os.makedirs(out, exist_ok=True)
    host = urllib.parse.urlsplit(start).netloc.lower().removeprefix("www.")
    q, seen, pages, docs, blocked = deque([(start, 0)]), {start}, [], {}, False
    while q and len(pages) < maxp:
        url, depth = q.popleft()
        time.sleep(1)
        try:
            links, raw = render_links(url)
        except subprocess.TimeoutExpired:
            continue
        if CHALLENGE.search(raw[:50000]):
            blocked = True
            break
        pages.append({"url": url, "depth": depth, "title": ""})
        for u, t in links:
            if DOC.search(u):
                docs.setdefault(u, {"url": u, "text": t, "found_on": url})
            elif (urllib.parse.urlsplit(u).netloc.lower().removeprefix("www.") == host and depth < 2
                  and u.split("#")[0] not in seen and HINT.search(u + " " + t)):
                seen.add(u.split("#")[0])
                q.append((u.split("#")[0], depth + 1))
    for name, rows, fields in (("doc_links.csv", list(docs.values()), ["url", "text", "found_on"]),
                               ("pages.csv", pages, ["url", "depth", "title"])):
        with open(os.path.join(out, name), "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=fields)
            w.writeheader(); w.writerows(rows)
    s = {"start": start, "slug": slug, "method": "obscura-render", "blocked": blocked, "pages": len(pages),
         "doc_links": len(docs), "queued_left": len(q)}
    json.dump(s, open(os.path.join(out, "summary.json"), "w"), indent=1)
    print(json.dumps(s))


if __name__ == "__main__":
    main()
