#!/usr/bin/env python3
"""Crawl igod.gov.in (Integrated Government Online Directory, NIC) into a
yellow-pages index of Indian government organizations.

Phase A (this script):
  1. BFS the category/state seed pages to discover every listing page
     (URLs ending in /organizations).
  2. For each listing page, parse the static rows and pull the rest through
     the lazy-load endpoint  <listing>/organizations_list_more/<start>/5.
  3. Write data/organizations_index.csv with one row per organization:
     branch, state, category, name, igod org id (if a detail page exists),
     website URL.

Phase B is igod_org_details.py (contacts + who's-who per organization).
"""
import csv
import re
import sys
import time
from collections import deque
from pathlib import Path
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

BASE = "https://igod.gov.in"
OUT = Path(__file__).resolve().parent.parent / "data" / "organizations_index.csv"
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0 Safari/537.36")
DELAY = 0.25          # politeness delay between requests
CHUNK = 5             # only limit<=5 is accepted by organizations_list_more

SEEDS = [
    f"{BASE}/categories",
    f"{BASE}/ug/categories",
    f"{BASE}/apx/categories",
    f"{BASE}/jud/categories",
    f"{BASE}/leg/categories",
    f"{BASE}/int/categories",
    f"{BASE}/sg/states",
    f"{BASE}/sg/district/states",
]

# pages worth expanding further (category / state index pages)
EXPAND_RE = re.compile(r"https://igod\.gov\.in/[a-z]+(/[A-Za-z0-9_]+)*/(categories|states)$")
LISTING_RE = re.compile(r"https://igod\.gov\.in/[a-z]+(/[A-Za-z0-9_]+)*/organizations$")
ORG_RE = re.compile(r"https://igod\.gov\.in/organization/([A-Za-z0-9_-]{15,})$")

session = requests.Session()
session.headers.update({"User-Agent": UA})


def get(url, **kw):
    for attempt in range(3):
        try:
            r = session.get(url, timeout=60, **kw)
            if r.status_code == 200:
                return r
        except requests.RequestException as e:
            print(f"  retry {attempt+1} {url}: {e}", file=sys.stderr)
        time.sleep(2 * (attempt + 1))
    return None


def discover_listings():
    """BFS seed pages -> set of listing URLs plus breadcrumb labels."""
    seen, listings = set(), {}
    q = deque(SEEDS)
    while q:
        url = q.popleft()
        if url in seen:
            continue
        seen.add(url)
        r = get(url)
        if r is None:
            continue
        time.sleep(DELAY)
        soup = BeautifulSoup(r.text, "html.parser")
        for a in soup.find_all("a", href=True):
            href = a["href"].split("?")[0].rstrip("/")
            if LISTING_RE.match(href):
                label = " ".join(a.get_text(" ", strip=True).split())
                # keep first non-empty label seen for this listing
                if href not in listings or (label and not listings[href]):
                    listings[href] = label
            elif EXPAND_RE.match(href) and href not in seen:
                q.append(href)
        print(f"discovered so far: {len(listings)} listings ({len(seen)} pages walked)", file=sys.stderr)
    return listings


def parse_rows(html):
    """Extract (name, org_id, website) tuples from listing/lazy-load HTML."""
    soup = BeautifulSoup(html, "html.parser")
    rows = []
    for div in soup.select("div.search-result-row"):
        name, org_id, website = None, None, None
        for a in div.find_all("a", href=True):
            href = a["href"].strip()
            m = ORG_RE.match(href)
            text = " ".join(a.get_text(" ", strip=True).split())
            if m:
                org_id = m.group(1)
                name = name or text
            elif href.startswith("http") and "igod.gov.in" not in href:
                website = href
                name = name or text
        if name:
            rows.append((name, org_id, website))
    return rows


PAGEVAR_RE = {
    "count": re.compile(r"var count='(\d+)'"),
    "first": re.compile(r"var items_on_first_page = '(\d+)'"),
}


def crawl_listing(url, label):
    r = get(url)
    if r is None:
        return []
    time.sleep(DELAY)
    rows = parse_rows(r.text)
    count = int(PAGEVAR_RE["count"].search(r.text).group(1)) if PAGEVAR_RE["count"].search(r.text) else len(rows)
    first = int(PAGEVAR_RE["first"].search(r.text).group(1)) if PAGEVAR_RE["first"].search(r.text) else len(rows)
    start = max(first, len(rows))
    while start < count:
        limit = min(CHUNK, count - start)
        more = get(f"{url}_list_more/{start}/{limit}", params={"keyword": ""},
                   headers={"X-Requested-With": "XMLHttpRequest",
                            "Accept": "text/html, */*; q=0.01", "Referer": url})
        if more is None or "search-result-row" not in more.text:
            print(f"  ! lazy-load stopped at {start}/{count} for {url}", file=sys.stderr)
            break
        rows.extend(parse_rows(more.text))
        start += limit
        time.sleep(DELAY)
    # classify from URL: /ug/CAT /sg/ST/CAT /apx/... /jud /leg /int
    parts = urlparse(url).path.strip("/").split("/")
    branch = parts[0]
    state = parts[1] if branch in ("sg", "apx") and len(parts) > 2 and len(parts[1]) == 2 else ""
    category = parts[-2] if len(parts) >= 2 else ""
    return [{"branch": branch, "state": state, "category_code": category,
             "category": label, "name": n, "igod_org_id": oid or "",
             "website": w or "", "listing_url": url}
            for n, oid, w in rows]


def main():
    listings = discover_listings()
    print(f"total listing pages: {len(listings)}", file=sys.stderr)
    all_rows, done = [], 0
    for url, label in sorted(listings.items()):
        rows = crawl_listing(url, label)
        all_rows.extend(rows)
        done += 1
        print(f"[{done}/{len(listings)}] {url} -> {len(rows)} orgs (total {len(all_rows)})", file=sys.stderr)
    # dedupe (same org can appear under multiple categories -> keep all category
    # tags but collapse exact duplicate rows)
    seen, uniq = set(), []
    for row in all_rows:
        key = (row["branch"], row["state"], row["category_code"], row["name"],
               row["igod_org_id"], row["website"])
        if key not in seen:
            seen.add(key)
            uniq.append(row)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(uniq[0].keys()))
        w.writeheader()
        w.writerows(uniq)
    print(f"wrote {len(uniq)} rows -> {OUT}", file=sys.stderr)


if __name__ == "__main__":
    main()
