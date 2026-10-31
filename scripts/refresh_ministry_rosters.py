#!/usr/bin/env python3
"""Re-run the union-ministry who's-who scrape with the wider page probes learnt on state sites, and MERGE the
result into data/ministry_officials.csv (a ministry's roster is replaced only when the new scrape found one)."""
import re, sys
from pathlib import Path
import pandas as pd
sys.path.insert(0, str(Path(__file__).resolve().parent))
import ministry_whoswho as W

W.PROBE_PATHS = list(dict.fromkeys(W.PROBE_PATHS + [
    "/en/whos-who/", "/whos-who/", "/officers", "/officials", "/key-officials", "/key-officers", "/our-officers",
    "/officers-list", "/directory", "/telephone-directory", "/contact-us", "/contacts", "/staff-directory",
    "/organisation", "/organization", "/administration", "/about-us/officers", "/about-us/organisation",
    "/about/whos-who", "/en/officers", "/Pages/whos-who.aspx", "/Page/WhosWho.aspx", "/whos-who.aspx",
    "/en/directory", "/officers-directory", "/en/key-officials", "/en/administration", "/about-us/organisation-chart",
    "/who-s-who-0", "/en/about-us/whos-who", "/en/who-s-who", "/about-us/who-s-who-0"]))
W.WHO_RE = re.compile(r"who[\s_'’%2-]*(i?s)?[\s_'’%27-]*who|officers?\b|officials|directory|key[- ]official", re.I)
OLD = W.OUT
NEW = W.DATA / "ministry_officials_new.csv"
W.OUT = NEW
W.main()
new = pd.read_csv(NEW) if NEW.exists() else pd.DataFrame()
old = pd.read_csv(OLD)
new = new[new.name.notna() & (new.name.astype(str).str.strip() != "")] if len(new) else new
# a ministry's roster is replaced only when the new scrape is at least as large (a 1-row contact page must not
# overwrite a 100-row who's-who)
oc = old.groupby("ministry").size(); nc = new.groupby("ministry").size() if len(new) else pd.Series(dtype=int)
got = {m for m in nc.index if nc[m] >= max(5, oc.get(m, 0) // 2)} | ({m for m in nc.index if m not in oc.index} if len(new) else set())
merged = pd.concat([old[~old.ministry.isin(got)], new], ignore_index=True)
merged.to_csv(OLD, index=False)
print(f"merged: old {old.ministry.nunique()} ministries / {len(old)} rows; new scrape {len(got)} ministries / {len(new)} rows; "
      f"result {merged.ministry.nunique()} ministries / {len(merged)} rows", file=sys.stderr)
