#!/usr/bin/env python3
"""Polite same-site crawler for server-rendered ministry websites (Drupal, NIC CMS, custom HTML).

Collects every link to a document (pdf/doc/docx/xls/xlsx/csv/zip/ppt) with its anchor text and the page it was
found on, plus each crawled page's title. Uses curl (macOS curl negotiates the old TLS versions several
.gov.in servers still require). Respects robots.txt, one request per second, max depth 3, max pages per site.
Stops on a host that serves a bot challenge (never bypassed).
Usage: crawl_html.py <start_url> <slug> [--max-pages 300] [--insecure]
Writes data/sites/<slug>/{doc_links.csv,pages.csv,summary.json}.
"""
import csv, html, json, os, re, subprocess, sys, time, urllib.parse, urllib.robotparser
from collections import deque

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0 Safari/537.36"
HERE = os.path.dirname(os.path.abspath(__file__))
DOC = re.compile(r"\.(pdf|docx?|xlsx?|csv|zip|pptx?|odt|ods)(?:$|[?#])", re.I)
SKIP = re.compile(r"\.(jpe?g|png|gif|svg|webp|ico|css|js|mp4|mp3|woff2?|ttf|eot)(?:$|[?#])|/(?:hi|hindi)/|"
                  r"[?&](?:lang=hi|print=|share=|sort=|order=)|mailto:|javascript:|tel:|/calendar|/feed|/rss", re.I)
CHALLENGE = re.compile(r"(?is)just a moment\.\.\.|challenge-platform|cf-chl-|client challenge|"
                       r"verify (?:that )?you(?:'| a)re (?:not a robot|human)")
NAV_HINT = re.compile(r"(?i)document|report|publication|notification|circular|order|notice|guideline|scheme|"
                      r"policy|act|rule|statistic|data|annual|budget|press|tender|gazette|archive|whats-?new|"
                      r"om|minutes|monthly|achievement|progress|division|about|ministry")


def curl(url, insecure, timeout=40):
    cmd = ["curl", "-sL", "--compressed", "--max-time", str(timeout), "-A", UA, "-H", "Accept-Language: en",
           "-w", "\n__META__%{http_code}\t%{content_type}\t%{url_effective}", url]
    if insecure:
        cmd.insert(1, "-k")
    p = subprocess.run(cmd, capture_output=True)
    body, _, meta = p.stdout.rpartition(b"\n__META__")
    parts = meta.decode("utf-8", "ignore").split("\t", 2)  # tab: content types contain spaces
    code = int(parts[0]) if parts and parts[0].isdigit() else 0
    return code, (parts[1] if len(parts) > 1 else ""), body, (parts[2] if len(parts) > 2 else url)


def norm(u):
    s = urllib.parse.urlsplit(u)
    return urllib.parse.urlunsplit((s.scheme, s.netloc.lower(), s.path or "/", s.query, ""))


def main():
    start, slug = sys.argv[1], sys.argv[2]
    max_pages = int(sys.argv[sys.argv.index("--max-pages") + 1]) if "--max-pages" in sys.argv else 300
    insecure = "--insecure" in sys.argv
    out = os.path.join(HERE, "..", "data", "sites", slug)
    os.makedirs(out, exist_ok=True)
    host = urllib.parse.urlsplit(start).netloc.lower()
    hosts = {host, host[4:] if host.startswith("www.") else "www." + host}
    rp = urllib.robotparser.RobotFileParser()
    c, _, body, _ = curl(f"{urllib.parse.urlsplit(start).scheme}://{host}/robots.txt", insecure, 20)
    rp.parse(body.decode("utf-8", "ignore").splitlines() if c == 200 else [])
    q, seen, pages, docs, last = deque([(start, 0)]), {norm(start)}, [], {}, 0.0
    summary = {"start": start, "slug": slug, "blocked": False, "errors": 0, "retried_ok": 0}
    failed, retry_pass = [], False
    while (q and len(pages) < max_pages) or (not q and failed and not retry_pass):
        if not q:  # one retry pass over pages that failed (timeouts, 5xx), after a pause
            retry_pass = True
            time.sleep(30)
            q.extend(failed)
            failed = []
            continue
        url, depth = q.popleft()
        if not rp.can_fetch(UA, url):
            continue
        wait = (3.0 if retry_pass else 1.0) - (time.time() - last)
        if wait > 0:
            time.sleep(wait)
        last = time.time()
        code, ctype, body, final = curl(url, insecure, 60 if retry_pass else 40)
        if code != 200 or "html" not in ctype:
            if code != 200:
                if retry_pass:
                    summary["errors"] += 1
                    failed.append((url, depth, code))
                elif code in (0, 408, 429, 500, 502, 503, 504):
                    failed.append((url, depth))
                else:
                    summary["errors"] += 1
            continue
        summary["retried_ok"] += retry_pass
        s = body.decode("utf-8", "ignore")
        if CHALLENGE.search(s[:100000]):
            summary["blocked"] = True
            break
        t = re.search(r"(?is)<title[^>]*>(.*?)</title>", s)
        pages.append({"url": final, "depth": depth, "title": html.unescape(re.sub(r"\s+", " ", t.group(1))).strip()[:200] if t else ""})
        for m in re.finditer(r'(?is)<a\b[^>]*?href\s*=\s*["\']([^"\'#]+)["\'][^>]*>(.*?)</a>', s):
            href, text = m.group(1).strip(), html.unescape(re.sub(r"<[^>]+>|\s+", " ", m.group(2))).strip()[:300]
            u = urllib.parse.urljoin(final, href)
            if not u.startswith("http"):
                continue
            if DOC.search(u):
                docs.setdefault(u, {"url": u, "text": text, "found_on": final})
                continue
            if urllib.parse.urlsplit(u).netloc.lower() not in hosts or SKIP.search(u) or depth >= 3:
                continue
            n = norm(u)
            if n in seen:
                continue
            seen.add(n)
            # crawl document-ish sections first
            (q.appendleft if NAV_HINT.search(u + " " + text) else q.append)((u, depth + 1))
    with open(os.path.join(out, "doc_links.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["url", "text", "found_on"])
        w.writeheader(); w.writerows(docs.values())
    with open(os.path.join(out, "pages.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["url", "depth", "title"])
        w.writeheader(); w.writerows(pages)
    with open(os.path.join(out, "failed.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["url", "depth", "status"])
        w.writerows(x if len(x) == 3 else (*x, "not retried") for x in failed)
    summary.update(pages=len(pages), doc_links=len(docs), queued_left=len(q), still_failed=len(failed))
    json.dump(summary, open(os.path.join(out, "summary.json"), "w"), indent=1)
    print(json.dumps(summary))


if __name__ == "__main__":
    main()
