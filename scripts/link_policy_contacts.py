#!/usr/bin/env python3
"""Link open policies/schemes to the government contact persons who own them.

Joins three datasets on normalized ministry names:
  1. digital-twin-for-ipa layers/13_flat_instrument_index.json (312 incentive
     instruments, free-text status) -> which policies are OPEN
  2. india-trade-sector-policy-recommendations data/pib_index.sqlite
     (~123k PIB releases by ministry x date) -> which ministries are ACTIVE
  3. this repo's data/officials.csv (igod who's-who) -> WHO to contact

Outputs:
  data/policy_contacts.csv       one row per (open instrument x ranked official)
  data/pib_ministry_contacts.csv ministry PIB activity (90d) x top contacts
"""
import csv
import difflib
import json
import re
import sqlite3
import sys
from collections import defaultdict
from datetime import date, timedelta
from pathlib import Path

HOME = Path.home()
DATA = Path(__file__).resolve().parent.parent / "data"
TWIN = HOME / "digital-twin-for-ipa" / "layers" / "13_flat_instrument_index.json"
PIB = HOME / "india-trade-sector-policy-recommendations" / "data" / "pib_index.sqlite"

# twin `offering_entity` / PIB shorthand -> canonical ministry name (igod style)
ALIASES = {
    "meity": "ministry of electronics and information technology",
    "moca": "ministry of civil aviation",
    "mod (ddp/drdo)": "ministry of defence",
    "moefcc": "ministry of environment forest and climate change",
    "mhi": "ministry of heavy industries",
    "mnre": "ministry of new and renewable energy",
    "mdoner": "ministry of development of north eastern region",
    "msde (+ labour employer-facing)": "ministry of skill development and entrepreneurship",
    "dot": "ministry of communications",
    "dpiit": "ministry of commerce and industry",
    "dept of commerce / dgft": "ministry of commerce and industry",
    "dept of fertilizers": "ministry of chemicals and fertilizers",
    "dept of pharmaceuticals": "ministry of chemicals and fertilizers",
    "dfpd (food and pd)": "ministry of consumer affairs food and public distribution",
    "fahd (fisheries/ahd)": "ministry of fisheries animal husbandry and dairying",
    "dae": "department of atomic energy",
    "ministry of i and b": "ministry of information and broadcasting",
    "ministry of finance (dea/dfs/ifsca/ncgtc)": "ministry of finance",
    "external affairs": "ministry of external affairs",
    "home affairs": "ministry of home affairs",
    "law and justice": "ministry of law and justice",
    "minority affairs": "ministry of minority affairs",
    "culture": "ministry of culture",
    "health and family welfare": "ministry of health and family welfare",
    "agriculture and farmers welfare": "ministry of agriculture and farmers welfare",
}

RANK = ["cabinet minister", "minister of state", "minister", "secretary",
        "additional secretary", "joint secretary", "director general",
        "director", "deputy secretary", "under secretary"]

OPEN_PAT = re.compile(r"active|in force|operative|current|listed|notified|open|live|administered",
                      re.I)
CLOSED_PAT = re.compile(r"closed|lapsed|superseded|unverif|not found|not verifiable|site down|stale",
                        re.I)


def norm(s):
    s = (s or "").lower().replace("&", " and ")
    s = re.sub(r"[^a-z ]", " ", s)
    s = re.sub(r"\b(the|govt|government|of india)\b", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return ALIASES.get(s, s)


def rank_of(designation):
    d = (designation or "").lower()
    for i, r in enumerate(RANK):
        if r in d:
            return i
    return len(RANK)


def is_open(inst):
    text = " ".join(str(inst.get(k, "")) for k in ("status", "application_status",
                                                   "what_companies_get"))
    if CLOSED_PAT.search(text) and not OPEN_PAT.search(text):
        return False
    return bool(OPEN_PAT.search(text)) or inst.get("verified_on_site") is True


def load_officials():
    """normalized org name -> officials sorted by seniority."""
    by_org = defaultdict(list)
    with (DATA / "officials.csv").open() as f:
        for row in csv.DictReader(f):
            by_org[norm(row["org_name"])].append(row)
    for offs in by_org.values():
        offs.sort(key=lambda r: rank_of(r["designation"]))
    return by_org


def match_org(name, by_org):
    n = norm(name)
    if n in by_org:
        return n
    # containment then fuzzy
    for cand in by_org:
        if n and (n in cand or cand in n):
            return cand
    close = difflib.get_close_matches(n, list(by_org), n=1, cutoff=0.75)
    return close[0] if close else None


def main():
    by_org = load_officials()
    print(f"{len(by_org)} organizations with officials", file=sys.stderr)

    # --- 1. open instruments -> contacts -------------------------------
    twin = json.load(TWIN.open())["instruments"]
    out1 = DATA / "policy_contacts.csv"
    matched = unmatched = 0
    with out1.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["instrument", "offering_entity", "tier", "status",
                    "instrument_type", "source_url", "matched_org",
                    "contact_name", "designation", "division", "phones", "email"])
        for inst in twin:
            if not is_open(inst):
                continue
            org_key = match_org(inst.get("offering_entity", ""), by_org)
            status = inst.get("status") or inst.get("application_status") or "open (inferred)"
            base = [inst.get("instrument"), inst.get("offering_entity"),
                    inst.get("tier"), status[:120], inst.get("instrument_type"),
                    inst.get("source_url", "")]
            if org_key:
                matched += 1
                for off in by_org[org_key][:5]:
                    w.writerow(base + [off["org_name"], off["name"], off["designation"],
                                       off["division"], off["phones"], off["email"]])
            else:
                unmatched += 1
                w.writerow(base + ["", "", "", "", "", ""])
    print(f"instruments: {matched} matched, {unmatched} unmatched -> {out1}", file=sys.stderr)

    # --- 2. PIB 90-day ministry activity -> contacts --------------------
    con = sqlite3.connect(PIB)
    since = (date.today() - timedelta(days=90)).isoformat()
    rows = con.execute(
        "SELECT ministry, count(*) n, max(date) latest, "
        "       (SELECT title FROM pib_items p2 WHERE p2.ministry=p1.ministry "
        "        ORDER BY date DESC, id DESC LIMIT 1) latest_title "
        "FROM pib_items p1 WHERE date >= ? GROUP BY ministry ORDER BY n DESC", (since,)).fetchall()
    out2 = DATA / "pib_ministry_contacts.csv"
    pib_matched = 0
    with out2.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["ministry", "releases_90d", "latest_release_date", "latest_release_title",
                    "matched_org", "contact_name", "designation", "phones", "email"])
        for ministry, n, latest, title in rows:
            org_key = match_org(ministry, by_org)
            base = [ministry, n, latest, (title or "")[:160]]
            if org_key:
                pib_matched += 1
                for off in by_org[org_key][:3]:
                    w.writerow(base + [off["org_name"], off["name"],
                                       off["designation"], off["phones"], off["email"]])
            else:
                w.writerow(base + ["", "", "", "", ""])
    print(f"PIB ministries (90d): {len(rows)} total, {pib_matched} matched -> {out2}",
          file=sys.stderr)


if __name__ == "__main__":
    main()
