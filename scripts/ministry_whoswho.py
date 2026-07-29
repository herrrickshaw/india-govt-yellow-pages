#!/usr/bin/env python3
"""Tier-2 scrape: each union ministry/department's OWN who's-who page.

igod's officer directory only covers ~130 orgs at 2-3 officials each; the
ministries' own /whos-who pages (standard NIC Drupal 'views-table' markup)
list the full officer roster with room/phone/email.

Discovery per ministry website:
  1. quick links on the igod org detail page containing 'who'
  2. common-path probes (/about-us/whos-who, /whos-who, ...)
  3. dead .nic.in domains retried as .gov.in

Parsing: any <table> whose header row has a Name column plus a
Designation-like column; column roles mapped from header text. Falls back
across all tables on the page. Emails de-obfuscated ([at]/[dot]/[in]).

Output: data/ministry_officials.csv
"""
import csv
import re
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

DATA = Path(__file__).resolve().parent.parent / "data"
OUT = DATA / "ministry_officials.csv"
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0 Safari/537.36")
PROBE_PATHS = ["/about-us/whos-who", "/whos-who", "/about-us/who-s-who",
               "/whoswho", "/en/whos-who", "/content/whos-who",
               "/about-us/whos-who-0", "/who-s-who", "/aboutus/whos-who",
               "/who-is-who", "/about-us/who-is-who", "/whoiswho"]
WHO_RE = re.compile(r"who[\s_'’%2-]*(i?s)?[\s_'’%27-]*who", re.I)

session = requests.Session()
session.headers.update({"User-Agent": UA})


def get(url, timeout=25):
    try:
        r = session.get(url, timeout=timeout, verify=False, allow_redirects=True)
        if r.status_code == 200:
            return r
    except requests.RequestException:
        # dead .nic.in domains often live on as .gov.in
        if ".nic.in" in url:
            try:
                r = session.get(url.replace(".nic.in", ".gov.in"), timeout=timeout,
                                verify=False, allow_redirects=True)
                if r.status_code == 200:
                    return r
            except requests.RequestException:
                pass
    return None


def deob(text):
    t = re.sub(r"\s*\[\s*at\s*\]\s*", "@", text or "", flags=re.I)
    t = re.sub(r"\s*\[\s*dot\s*\]\s*", ".", t, flags=re.I)
    t = re.sub(r"\[\s*in\s*\]\s*$", ".in", t.strip(), flags=re.I)  # gov[in]
    t = re.sub(r"\[|\]", "", t)
    return t.strip(" .,;")


def clean(s):
    return " ".join((s or "").split())


COLROLE = [
    ("name", re.compile(r"\bname|officer\b", re.I)),
    ("designation", re.compile(r"desig|post|rank", re.I)),
    ("division", re.compile(r"division|section|wing|department|branch|subject|work", re.I)),
    ("room", re.compile(r"room", re.I)),
    ("phone", re.compile(r"tel|phone|contact|intercom|mobile|fax|std|office no", re.I)),
    ("email", re.compile(r"mail", re.I)),
    ("address", re.compile(r"address", re.I)),
]

EMAIL_RE = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-z]{2,}")
SKIP_NAME = re.compile(r"^(s\.?\s*no\.?|sr\.?|#|\d+\.?|vacant|-*)$", re.I)


def parse_tables(html, page_url):
    soup = BeautifulSoup(html, "html.parser")
    out = []
    for table in soup.find_all("table"):
        header_cells = None
        thead = table.find("thead")
        if thead:
            header_cells = thead.find_all(["th", "td"])
        else:
            first = table.find("tr")
            if first and first.find("th"):
                header_cells = first.find_all(["th", "td"])
        if not header_cells:
            continue
        roles = {}
        for idx, cell in enumerate(header_cells):
            text = clean(cell.get_text(" "))
            for role, pat in COLROLE.items() if isinstance(COLROLE, dict) else COLROLE:
                if pat.search(text) and role not in roles.values():
                    roles[idx] = role
                    break
        if "name" not in roles.values() or "designation" not in roles.values():
            continue
        caption = clean(table.caption.get_text(" ")) if table.caption else ""
        body = table.find("tbody") or table
        for tr in body.find_all("tr"):
            cells = tr.find_all("td")
            if not cells:
                continue
            rec = {"division": caption, "phones": [], "email": "", "name": "",
                   "designation": "", "room": "", "address": ""}
            for idx, cell in enumerate(cells):
                role = roles.get(idx)
                if not role:
                    continue
                val = clean(cell.get_text(" "))
                if role == "phone":
                    if val and not SKIP_NAME.match(val):
                        rec["phones"].append(val)
                elif role == "email":
                    rec["email"] = deob(val) or ""
                elif role == "division" and caption:
                    rec["address"] = rec["address"] or val
                else:
                    if not rec.get(role):
                        rec[role] = val
            name = clean(rec["name"])
            if not name or SKIP_NAME.match(name) or len(name) < 3:
                continue
            if not EMAIL_RE.match(rec["email"] or ""):
                m = EMAIL_RE.search(deob(clean(tr.get_text(" "))))
                rec["email"] = m.group(0) if m else rec["email"]
            out.append({"division": rec["division"], "name": name,
                        "designation": rec["designation"], "room": rec["room"],
                        "phones": "; ".join(rec["phones"])[:200],
                        "email": rec["email"], "source_url": page_url})
    return out


def find_whoswho_urls(website, quick_links):
    urls = [u for u in quick_links if WHO_RE.search(u)]
    if urls:
        return urls
    base = website.rstrip("/")
    found = []
    for path in PROBE_PATHS:
        r = get(base + path)
        if r is not None and WHO_RE.search(r.url + r.text[:4000]):
            found.append(r.url)
            break
        time.sleep(0.1)
    if not found:
        # last resort: scan homepage nav for a who's-who link
        r = get(base)
        if r is not None:
            soup = BeautifulSoup(r.text, "html.parser")
            for a in soup.find_all("a", href=True):
                if WHO_RE.search(a["href"]) or WHO_RE.search(a.get_text(" ")):
                    found.append(urljoin(r.url, a["href"]))
                    break
    return found[:2]


def quick_links_for(org_id):
    r = get(f"https://igod.gov.in/organization/{org_id}")
    if r is None:
        return []
    return re.findall(r'href="(https?://[^"]+)"', r.text.split("Quick Links")[-1]
                      .split("Organizations Under")[0]) if "Quick Links" in r.text else []


PHONE_RE = re.compile(r"(?:\+91[-\s]?)?(?:011[-\s]?)?\d{7,11}")


def parse_pdf(content, page_url):
    """Extract officials from a who's-who PDF via pdfplumber tables, falling
    back to line-wise name/designation/email heuristics."""
    import io
    import pdfplumber
    out = []
    try:
        with pdfplumber.open(io.BytesIO(content)) as pdf:
            for page in pdf.pages[:60]:
                for table in (page.extract_tables() or []):
                    if not table or len(table[0] or []) < 2:
                        continue
                    header = [clean(str(c or "")) for c in table[0]]
                    roles = {}
                    for idx, text in enumerate(header):
                        for role, pat in COLROLE:
                            if pat.search(text) and role not in roles.values():
                                roles[idx] = role
                                break
                    if "name" not in roles.values():
                        continue
                    for row in table[1:]:
                        rec = {"division": "", "name": "", "designation": "",
                               "room": "", "phones": [], "email": ""}
                        for idx, cell in enumerate(row):
                            role = roles.get(idx)
                            val = clean(str(cell or ""))
                            if not role or not val:
                                continue
                            if role == "phone":
                                rec["phones"].append(val)
                            elif role == "email":
                                rec["email"] = deob(val)
                            elif not rec.get(role):
                                rec[role] = val
                        if rec["name"] and not SKIP_NAME.match(rec["name"]) \
                                and len(rec["name"]) >= 3:
                            out.append({"division": rec["division"], "name": rec["name"],
                                        "designation": rec["designation"],
                                        "room": rec["room"],
                                        "phones": "; ".join(rec["phones"])[:200],
                                        "email": rec["email"], "source_url": page_url})
                if out:
                    continue
                # heuristic fallback: lines that pair a Shri/Smt/Dr name with an email
                for line in (page.extract_text() or "").splitlines():
                    m = re.match(r"\s*\d*\.?\s*((?:Shri|Smt\.?|Dr\.?|Ms\.?|Mr\.?)\s+[A-Z][A-Za-z. ]{3,40})[,\s]+(.{3,60}?)\s+([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+|\S+\[at\]\S+)",
                                 line)
                    if m:
                        out.append({"division": "", "name": clean(m.group(1)),
                                    "designation": clean(m.group(2)), "room": "",
                                    "phones": "; ".join(PHONE_RE.findall(line)[:3]),
                                    "email": deob(m.group(3)), "source_url": page_url})
    except Exception as e:
        print(f"  pdf parse failed {page_url}: {e}", file=sys.stderr)
    return out


def parse_nextjs(html, base_url):
    """JS-shell (Next.js) sites: pull /_next/data/<buildId>/<path>.json and
    parse any HTML tables embedded in the JSON payload."""
    import json as _json
    m = re.search(r'__NEXT_DATA__"[^>]*>(.*?)</script>', html, re.S)
    if not m:
        return []
    try:
        build = _json.loads(m.group(1)).get("buildId")
    except _json.JSONDecodeError:
        return []
    if not build:
        return []
    p = urlparse(base_url)
    path = p.path.strip("/") or "index"
    r = get(f"{p.scheme}://{p.netloc}/_next/data/{build}/{path}.json?parentslug={path}")
    if r is None:
        return []
    # collect every string in the JSON that carries an HTML table
    frags = re.findall(r'"((?:[^"\\]|\\.)*<table(?:[^"\\]|\\.)*)"', r.text)
    out = []
    for frag in frags:
        out.extend(parse_tables(frag.encode().decode("unicode_escape"), base_url))
    return out


def scrape_ministry(row):
    name, website, org_id = row["name"], row["website"], row["igod_org_id"]
    links = quick_links_for(org_id) if org_id else []
    urls = find_whoswho_urls(website, links)
    officials, used = [], ""
    for u in urls:
        r = get(u)
        if r is None:
            continue
        ctype = r.headers.get("Content-Type", "")
        if u.lower().endswith(".pdf") or "pdf" in ctype:
            got = parse_pdf(r.content, u)
        else:
            got = parse_tables(r.text, u)
            if not got and "__NEXT_DATA__" in r.text:
                got = parse_nextjs(r.text, u)
            if not got:
                # page may link straight to a who's-who PDF
                soup = BeautifulSoup(r.text, "html.parser")
                for a in soup.find_all("a", href=True):
                    href = a["href"]
                    if href.lower().endswith(".pdf") and (WHO_RE.search(href)
                                                          or WHO_RE.search(a.get_text(" "))):
                        rp = get(urljoin(r.url, href))
                        if rp is not None:
                            got = parse_pdf(rp.content, rp.url)
                            if got:
                                break
        if got:
            officials, used = got, u
            break
    return name, website, used, officials


def main():
    requests.packages.urllib3.disable_warnings()
    seen, targets = set(), []
    with (DATA / "organizations_index.csv").open() as f:
        for row in csv.DictReader(f):
            if (row["branch"] == "ug" and row["category_code"] in ("E002", "E003", "E053")
                    and row["website"] and row["website"] not in seen):
                seen.add(row["website"])
                targets.append(row)
    print(f"{len(targets)} ministry/department websites", file=sys.stderr)

    results = []
    with ThreadPoolExecutor(max_workers=8) as ex:
        for i, (name, website, used, offs) in enumerate(
                ex.map(scrape_ministry, targets), 1):
            print(f"[{i}/{len(targets)}] {name}: {len(offs)} officials "
                  f"{'(' + used + ')' if used else '(no whos-who found)'}", file=sys.stderr)
            for o in offs:
                results.append({"ministry": name, "website": website, **o})

    with OUT.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["ministry", "website", "division", "name",
                                          "designation", "room", "phones", "email",
                                          "source_url"])
        w.writeheader()
        w.writerows(results)
    print(f"wrote {len(results)} officials -> {OUT}", file=sys.stderr)


if __name__ == "__main__":
    main()
