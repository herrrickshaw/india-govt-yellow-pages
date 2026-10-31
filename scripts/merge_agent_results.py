#!/usr/bin/env python3
"""Merge the per-group agent outputs (data/agents/group*/officials.csv, sources.csv) into the repo:
  * officials -> data/ministry_officials.csv (a ministry's roster is replaced only by a larger one; new ministries added)
  * sources   -> data/agents/sources_all.csv (crawl seeds for ministry_documents/tools and signatory_matrix candidates)
Prints a per-ministry before/after table."""
import re, sys
from pathlib import Path
import pandas as pd

REPO = Path(__file__).resolve().parent.parent
COLS = ["ministry", "website", "division", "name", "designation", "room", "phones", "email", "source_url"]
offs, srcs = [], []
for g in sorted((REPO / "data/agents").glob("group*/")):
    p = g / "officials.csv"
    if p.exists():
        try:
            d = pd.read_csv(p, on_bad_lines="skip", dtype=str).fillna("")
            for c in COLS:
                if c not in d.columns:
                    d[c] = ""
            d = d[COLS]; d["agent_group"] = g.name; offs.append(d)
        except Exception as e:
            print(f"{p}: {e}", file=sys.stderr)
    p = g / "sources.csv"
    if p.exists():
        try:
            s = pd.read_csv(p, on_bad_lines="skip", dtype=str).fillna(""); s["agent_group"] = g.name; srcs.append(s)
        except Exception as e:
            print(f"{p}: {e}", file=sys.stderr)
if srcs:
    pd.concat(srcs, ignore_index=True).drop_duplicates("url").to_csv(REPO / "data/agents/sources_all.csv", index=False)
    print(f"sources: {sum(len(s) for s in srcs)} rows -> data/agents/sources_all.csv")
if not offs:
    print("no officials.csv yet"); sys.exit(0)
new = pd.concat(offs, ignore_index=True)
new = new[new.name.str.strip().str.len() > 2]
new["name"] = new.name.str.replace(r"\s+", " ", regex=True).str.strip()
new["email"] = new.email.str.replace(r"\[at\]|\(at\)", "@", regex=True).str.replace(r"\[dot\]|\(dot\)", ".", regex=True).str.strip()
new = new.drop_duplicates(["ministry", "name", "designation"])
old = pd.read_csv(REPO / "data/ministry_officials.csv", dtype=str).fillna("")
oc = old.groupby("ministry").size(); nc = new.groupby("ministry").size()
replace = {m for m in nc.index if nc[m] >= max(5, oc.get(m, 0))}
keep_old = old[~old.ministry.isin(replace)]
add_new = new[new.ministry.isin(replace)]
# ministries where the agent found fewer rows than the existing roster: append only officers not already present
small = new[~new.ministry.isin(replace)]
if len(small):
    key = lambda d: (d.ministry.str.lower() + "|" + d.name.str.lower().str.replace(r"[^a-z ]", "", regex=True).str.strip())
    small = small[~key(small).isin(set(key(old)))]
merged = pd.concat([keep_old, add_new, small], ignore_index=True)
merged.to_csv(REPO / "data/ministry_officials.csv", index=False)
rep = pd.DataFrame({"before": oc, "agent_found": nc}).fillna(0).astype(int)
rep["after"] = merged.groupby("ministry").size()
rep = rep.fillna(0).astype(int).sort_values("after", ascending=False)
print(rep.to_string())
print(f"ministry_officials.csv: {old.ministry.nunique()} -> {merged.ministry.nunique()} ministries, {len(old)} -> {len(merged)} rows")
