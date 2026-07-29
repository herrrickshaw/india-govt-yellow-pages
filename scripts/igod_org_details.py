#!/usr/bin/env python3
"""Phase B: for every igod organization detail page found by igod_crawl.py,
extract (a) the organization's own contact block and (b) the who's-who
officer directory (name, designation, division, phones, address, email).

Outputs:
  data/org_contacts.csv  — one row per organization
  data/officials.csv     — one row per listed official
"""
import csv
import html
import re
import sys
import time
from pathlib import Path

import requests
from bs4 import BeautifulSoup

BASE = "https://igod.gov.in"
DATA = Path(__file__).resolve().parent.parent / "data"
INDEX = DATA / "organizations_index.csv"
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0 Safari/537.36")
DELAY = 0.25
DIR_CHUNK = 10  # list_contacts per_page

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


def deobfuscate(text):
    """secy[dot]moc[at]nic[dot]in -> secy.moc@nic.in"""
    return re.sub(r"\s*\[dot\]\s*", ".", re.sub(r"\s*\[at\]\s*", "@", text, flags=re.I), flags=re.I).strip()


def clean(s):
    return " ".join(html.unescape(s or "").split())


def parse_contact_block(soup):
    out = {"address": "", "phone": "", "fax": "", "email": "", "website": "", "social": ""}
    txt = soup.get_text("\n")
    block = re.search(r"Contact Details(.*?)(Quick Links|Organizations Under|Organization Directory|Help us)", txt, re.S)
    if not block:
        return out
    b = block.group(1)
    for key, pat in [("address", r"Address:\s*(.*?)(?:\n\s*Phone No:|$)"),
                     ("phone", r"Phone No:\s*(.*?)(?:\n\s*Fax:|$)"),
                     ("fax", r"Fax:\s*(.*?)(?:\n\s*Email:|$)"),
                     ("email", r"Email:\s*(.*?)(?:\n\s*Social Media:|$)"),
                     ("website", r"Website:\s*(\S+)")]:
        m = re.search(pat, b, re.S)
        if m:
            out[key] = clean(m.group(1))
    out["email"] = deobfuscate(out["email"])
    return out


def parse_officials_rows(html_text):
    soup = BeautifulSoup(html_text, "html.parser")
    rows = []
    for tr in soup.find_all("tr"):
        tds = tr.find_all("td")
        if len(tds) < 4:
            continue
        name = clean(tds[0].get_text(" "))
        desig = clean(tds[1].get_text(" "))
        div = clean(tds[2].get_text(" "))
        contact_cell = tds[3]
        phones = ", ".join(a.get_text(strip=True) for a in contact_cell.find_all("a", href=re.compile("^tel:")))
        ctxt = contact_cell.get_text("\n")
        addr = clean(re.search(r"Address:\s*(.*)", ctxt, re.S).group(1)) if "Address:" in ctxt else ""
        email = ""
        if len(tds) >= 5:
            email = deobfuscate(clean(tds[4].get_text(" ")))
            m = tds[4].find("a", href=re.compile("^mailto:"))
            if m and not email:
                email = m["href"][7:]
        if name:
            rows.append({"name": name, "designation": desig, "division": div,
                         "phones": phones, "office_address": addr, "email": email})
    return rows


def fetch_org(org_id):
    url = f"{BASE}/organization/{org_id}"
    r = get(url)
    if r is None:
        return None, [], None
    time.sleep(DELAY)
    soup = BeautifulSoup(r.text, "html.parser")
    # canonical full name from the page <title> ("... : Organization Details : X")
    canonical = None
    if soup.title:
        parts = soup.title.get_text().split(":")
        if len(parts) >= 3:
            canonical = clean(parts[-1])
    contact = parse_contact_block(soup)
    officials = parse_officials_rows(r.text)
    m = re.search(r"var count='(\d+)'", r.text)
    count = int(m.group(1)) if m else len(officials)
    start = len(officials)
    while start < count:
        limit = min(DIR_CHUNK, count - start)
        more = get(f"{url}/list_contacts/{start}/{limit}",
                   headers={"X-Requested-With": "XMLHttpRequest",
                            "Accept": "text/html, */*; q=0.01", "Referer": url})
        if more is None:
            break
        got = parse_officials_rows(more.text)
        if not got:
            break
        officials.extend(got)
        start += limit
        time.sleep(DELAY)
    return contact, officials, canonical


def main():
    orgs = {}
    with INDEX.open() as f:
        for row in csv.DictReader(f):
            if row["igod_org_id"]:
                orgs.setdefault(row["igod_org_id"], row)
    print(f"{len(orgs)} organizations with igod detail pages", file=sys.stderr)

    cpath, opath = DATA / "org_contacts.csv", DATA / "officials.csv"
    cf = cpath.open("w", newline="")
    of = opath.open("w", newline="")
    cw = csv.DictWriter(cf, fieldnames=["igod_org_id", "org_name", "branch", "state",
                                        "address", "phone", "fax", "email", "website", "social"])
    ow = csv.DictWriter(of, fieldnames=["igod_org_id", "org_name", "branch", "state",
                                        "name", "designation", "division", "phones",
                                        "office_address", "email"])
    cw.writeheader()
    ow.writeheader()
    for i, (oid, meta) in enumerate(sorted(orgs.items()), 1):
        contact, officials, canonical = fetch_org(oid)
        base = {"igod_org_id": oid, "org_name": canonical or meta["name"],
                "branch": meta["branch"], "state": meta["state"]}
        if contact is not None:
            cw.writerow({**base, **contact})
        for off in officials:
            ow.writerow({**base, **off})
        cf.flush(); of.flush()
        print(f"[{i}/{len(orgs)}] {meta['name']}: {len(officials)} officials", file=sys.stderr)
    cf.close(); of.close()
    print(f"wrote {cpath} and {opath}", file=sys.stderr)


if __name__ == "__main__":
    main()
