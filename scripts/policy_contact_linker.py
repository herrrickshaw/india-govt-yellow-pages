#!/usr/bin/env python3
"""Who do I contact about this policy / incentive?  Links instruments to the officials who signed their paperwork.

Instruments come from two places:
  * the curated list in data/policy_windows.csv / data/policy_contacts.csv (open incentive instruments), and
  * the documents themselves: scheme / guideline / PLI / Yojana / Mission / Fund / Policy names found in order,
    notification, guideline and gazette titles (centre: data/signatories/; states: data/states/<ST>/).

For every instrument it collects the documents that mention it, the people who signed those documents (from the
signatory directories: designation, printed email/phone, roster match, latest known posting from the career tracker),
and roster officers whose division name matches the instrument.  Output:

  data/policy_contacts_from_documents.csv   one row per (instrument, contact) with evidence
  data/policy_instruments_index.csv         one row per instrument: ministry, documents, dates, top contacts
  data/POLICY_CONTACTS.md                   readable: per ministry, per instrument, the contacts and the documents

Run:  /usr/bin/python3 scripts/policy_contact_linker.py
"""
import re, sys, time
from collections import Counter, defaultdict
from pathlib import Path

import pandas as pd

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))
import signatory_matrix as S  # noqa: E402

STOP = {"the", "and", "for", "of", "in", "on", "to", "under", "scheme", "schemes", "guidelines", "guideline", "policy", "rules",
        "notification", "order", "regarding", "reg", "amendment", "amendments", "revised", "draft", "final", "new", "india",
        "indian", "national", "central", "government", "ministry", "department", "govt", "dated", "date", "year", "years", "2020",
        "2021", "2022", "2023", "2024", "2025", "2026", "phase", "part", "list", "download", "pdf", "click", "here", "component",
        "industrial", "investment", "package", "state", "studies", "study", "certification", "under", "with", "via", "new", "first",
        "second", "third", "nov", "dec", "jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "effective", "covers",
        "administered", "applied", "customized", "mega", "umbrella", "verticals", "roads", "two", "entrepreneurship"}
STATE_CODES = {"andhra pradesh": "AP", "arunachal pradesh": "AR", "assam": "AS", "bihar": "BR", "chhattisgarh": "CG", "goa": "GA", "gujarat": "GJ",
               "haryana": "HR", "himachal pradesh": "HP", "jharkhand": "JH", "karnataka": "KA", "kerala": "KL", "madhya pradesh": "MP",
               "maharashtra": "MH", "manipur": "MN", "meghalaya": "ML", "mizoram": "MZ", "nagaland": "NL", "odisha": "OD", "punjab": "PB",
               "rajasthan": "RJ", "sikkim": "SK", "tamil nadu": "TN", "telangana": "TS", "tripura": "TR", "uttar pradesh": "UP",
               "uttarakhand": "UK", "west bengal": "WB", "delhi": "DL", "jammu & kashmir": "JK", "jammu and kashmir": "JK", "ladakh": "LA",
               "puducherry": "PY", "chandigarh": "CH", "andaman": "AN", "lakshadweep": "LD", "j&k": "JK", "hp": "HP", "up": "UP", "mp": "MP",
               "ap": "AP", "tn": "TN"}
INSTR_PATTERNS = [
    re.compile(r"\b((?:PM|Pradhan Mantri)[- ][A-Z][A-Za-z\-]+(?:\s+[A-Z][A-Za-z\-]+){0,4})"),
    re.compile(r"\b((?:Production Linked Incentive|PLI)\s+(?:Scheme\s+)?(?:for\s+)?[A-Z][A-Za-z&,\- ]{3,60}?)(?=\s*[-–:(,.]|\s+(?:dated|under|reg|for the|on)\b|$)"),
    re.compile(r"\b([A-Z][A-Za-z0-9&'\-]+(?:\s+(?:of|for|and|&|on)?\s*[A-Z][A-Za-z0-9&'\-]+){0,6}\s+(?:Scheme|Yojana|Mission|Programme|Program|Fund|Abhiyan|Initiative|Package|Policy|Incentive Scheme|Challenge))\b"),
    re.compile(r"(?:Guidelines?|Operational Guidelines|Scheme Guidelines|SOPs?|Standard Operating Procedure)\s+(?:for|of|on|under)\s+(?:the\s+)?(?:implementation of\s+)?(?:the\s+)?([A-Z][A-Za-z0-9&'\-]+(?:\s+[A-Za-z0-9&'\-]+){1,7})"),
    re.compile(r"\b([A-Z]{3,8})\b\s*(?:Scheme|scheme|Guidelines|guidelines)"),
    re.compile(r"\b((?:Viability Gap Funding|Interest Subvention|Capital Subsidy|Credit Linked Capital Subsidy|Export Promotion Capital Goods|Remission of Duties|Duty Drawback|Advance Authori[sz]ation|Technology Upgradation Fund|Champion Services Sector|Design Linked Incentive|Startup India Seed Fund|Fund of Funds|Credit Guarantee)[A-Za-z &\-]{0,40})", re.I),
]


def instr_key(name):
    toks = [t for t in re.split(r"[^a-z0-9]+", str(name).lower()) if t and t not in STOP and len(t) > 2]
    return " ".join(toks)


def instruments_from_titles(docs):
    found = defaultdict(list)
    for r in docs.itertuples():
        text = f"{r.title} . {getattr(r, 'subject', '') or ''}"
        text = re.sub(r"\s+", " ", str(text))
        names = set()
        for pat in INSTR_PATTERNS:
            for m in pat.finditer(text):
                nm = m.group(1).strip(" -–:,.")
                if 6 <= len(nm) <= 90 and not re.search(r"\d{5,}|www\.|http", nm):
                    names.add(nm)
        for nm in names:
            k = instr_key(nm)
            if len(k) >= 5:
                found[k].append((nm, r.doc_id))
    rows = []
    for k, lst in found.items():
        ids = {d for _, d in lst}
        if len(ids) < 2:
            continue
        label = Counter(n for n, _ in lst).most_common(1)[0][0]
        rows.append(dict(instrument=label, key=k, source="documents", n_docs=len(ids), doc_ids=ids))
    return rows


def curated_instruments():
    rows = []
    for fn in ("policy_windows.csv", "policy_contacts.csv"):
        p = REPO / "data" / fn
        if not p.exists():
            continue
        d = pd.read_csv(p, on_bad_lines="skip")
        for ins in d.instrument.dropna().unique():
            k = instr_key(re.sub(r"\(.*?\)", "", ins))
            acr = [a for a in re.findall(r"\(([A-Z][A-Z0-9\-]{1,9})\)", ins) if a.lower() not in STOP]
            acr += [t for t in re.findall(r"\b([A-Z][A-Z0-9]{2,7})\b", re.sub(r"\(.*?\)", "", ins)) if t.lower() not in STOP and not t.isdigit()]
            ent = d[d.instrument == ins].get("offering_entity", pd.Series(dtype=str)).dropna().astype(str).head(1).tolist()
            ent_l = (ent[0].lower() if ent else "")
            state = next((c for n, c in STATE_CODES.items() if len(n) > 2 and n in ent_l), None) or (STATE_CODES.get(ent_l) if ent_l in STATE_CODES else None)
            if state is None:
                state = next((c for n, c in STATE_CODES.items() if len(n) > 3 and n in ins.lower()), None)
            rows.append(dict(instrument=ins, key=k, source="curated", acronyms=list(dict.fromkeys(acr)), offering_entity=ent, state=state))
    # instruments found by scripts/new_policy_scanner.py in PIB releases / ministry sites
    dp = REPO / "data/discovered_instruments.csv"
    if dp.exists():
        for r in pd.read_csv(dp).itertuples():
            ins = str(r.instrument)
            k = instr_key(ins)
            acr = [a for a in re.findall(r"\b([A-Z][A-Z0-9\-]{2,9})\b", ins) if a.lower() not in STOP]
            rows.append(dict(instrument=ins, key=k, source="pib/ministry-site", acronyms=acr, offering_entity=[str(r.ministry)], state=None))
    seen, out = set(), []
    for r in rows:
        if r["key"] in seen or len(r["key"]) < 4:
            continue
        seen.add(r["key"]); out.append(r)
    return out


def match_curated(ins, docs):
    """All distinctive tokens of the instrument name (>=2 of them) or one of its acronyms, as whole words; a state's
    instrument only matches that state's documents; a match covering >3% of all documents is too generic and dropped."""
    if ins.get("state"):
        docs = docs[docs.level == ins["state"]]
    if docs.empty:
        return set()
    toks = [t for t in ins["key"].split() if len(t) >= 3 and not t.isdigit()][:4]
    blob = (docs.title.fillna("") + " " + docs.get("subject", pd.Series("", index=docs.index)).fillna("")).str.lower()
    hit = pd.Series(False, index=docs.index)
    if len(toks) >= 2:
        hit |= pd.concat([blob.str.contains(rf"\b{re.escape(t)}" if len(t) > 4 else rf"\b{re.escape(t)}\b") for t in toks], axis=1).all(axis=1)
    other = [t for t in toks if t not in {a.lower() for a in ins.get("acronyms", [])}]
    for a in ins.get("acronyms", []):
        al = a.lower()
        if al in {"ppp", "pli", "psu", "cpse", "msme", "gst", "rti", "goi", "pmo", "ias", "ips", "new"}:
            # generic acronym: only together with another distinctive token of the name
            if other:
                hit |= blob.str.contains(rf"\b{re.escape(al)}\b") & pd.concat([blob.str.contains(rf"\b{re.escape(t)}") for t in other[:2]], axis=1).any(axis=1)
        elif len(a) >= 4 or (len(a) == 3 and not other):
            hit |= blob.str.contains(rf"\b{re.escape(al)}\b")
        elif len(a) == 3:
            hit |= blob.str.contains(rf"\b{re.escape(al)}\b") & pd.concat([blob.str.contains(rf"\b{re.escape(t)}") for t in other[:2]], axis=1).any(axis=1)
    if hit.sum() > max(40, 0.03 * len(docs)):
        return set()
    return set(docs[hit].doc_id)


def load_centre():
    out = REPO / "data/signatories"
    cand = pd.read_csv(out / "candidates.csv")
    sig = pd.read_csv(out / "signatures.csv") if (out / "signatures.csv").exists() else pd.DataFrame()
    d = pd.read_csv(out / "signatory_directory.csv") if (out / "signatory_directory.csv").exists() else pd.DataFrame()
    cand["level"] = "centre"
    subj = sig.drop_duplicates("doc_id")[["doc_id", "subject"]] if len(sig) else pd.DataFrame(columns=["doc_id", "subject"])
    cand = cand.merge(subj, on="doc_id", how="left")
    return cand, sig, d


def load_states():
    base = REPO / "data/states"
    cands, sigs, dirs = [], [], []
    for std in sorted(base.glob("*/")):
        st = std.name
        if len(st) != 2 or not (std / "candidates.csv").exists():
            continue
        c = pd.read_csv(std / "candidates.csv"); c["level"] = st
        if (std / "signatures.csv").exists():
            s = pd.read_csv(std / "signatures.csv"); s["level"] = st; sigs.append(s)
            c = c.merge(s.drop_duplicates("doc_id")[["doc_id", "subject"]], on="doc_id", how="left")
        cands.append(c)
        if (std / "signatory_directory.csv").exists():
            dd = pd.read_csv(std / "signatory_directory.csv"); dd["level"] = st; dirs.append(dd)
    return (pd.concat(cands, ignore_index=True) if cands else pd.DataFrame(),
            pd.concat(sigs, ignore_index=True) if sigs else pd.DataFrame(),
            pd.concat(dirs, ignore_index=True) if dirs else pd.DataFrame())


def main():
    cc, cs, cd = load_centre()
    sc, ss, sd = load_states()
    docs = pd.concat([cc, sc], ignore_index=True)
    sig = pd.concat([cs, ss], ignore_index=True)
    direc = pd.concat([cd.assign(level="centre"), sd], ignore_index=True)
    sig = sig[sig.sig_rank > 0] if len(sig) else sig
    if len(sig):
        sig["name_key"] = sig.signatory.astype(str).map(lambda x: " ".join(S.norm_tokens(x)))
    direc["name_key"] = direc.signatory.astype(str).map(lambda x: " ".join(S.norm_tokens(x)))
    dir_idx = {(r.level if r.level != "centre" else "centre", r.ministry, r.name_key): r for r in direc.itertuples()}
    rosters = pd.read_csv(REPO / "data/ministry_officials.csv")
    rosters["div_key"] = rosters.division.fillna("").astype(str).str.lower()

    # ---- instruments
    instr = curated_instruments()
    for ins in instr:
        ins["doc_ids"] = match_curated(ins, docs)
    instr += instruments_from_titles(docs)
    print(f"instruments: {sum(1 for i in instr if i['source']=='curated')} curated, {sum(1 for i in instr if i['source']=='documents')} from titles")

    sig_by_doc = defaultdict(list)
    for r in sig.itertuples():
        sig_by_doc[r.doc_id].append(r)
    docs["date"] = docs.date.astype(str).where(docs.date.astype(str).str.match(r"^(19[9]\d|20[0-2]\d)-"), None)
    doc_meta = docs.set_index("doc_id")

    contact_rows, index_rows = [], []
    for ins in instr:
        ids = [i for i in ins["doc_ids"] if i in doc_meta.index]
        if not ids:
            continue
        dm = doc_meta.loc[ids]
        ministries = dm.ministry.value_counts()
        level = dm.level.value_counts().index[0]
        people = defaultdict(lambda: dict(n=0, docs=[], desig=Counter(), email="", phone="", last=""))
        for did in ids:
            for s in sig_by_doc.get(did, []):
                key = (getattr(s, "level", "centre") if hasattr(s, "level") and isinstance(s.level, str) else "centre", doc_meta.loc[did, "ministry"], s.name_key)
                p = people[key]
                p["n"] += 1; p["docs"].append(did); p["desig"][str(s.sig_designation)] += 1
                em = getattr(s, "sig_email", "") if isinstance(getattr(s, "sig_email", ""), str) else ""
                ph = getattr(s, "sig_phone", "") if isinstance(getattr(s, "sig_phone", ""), str) else ""
                p["email"] = p["email"] or em; p["phone"] = p["phone"] or ph
                dt = str(doc_meta.loc[did, "date"]) if pd.notna(doc_meta.loc[did, "date"]) else ""
                p["last"] = max(p["last"], dt)
        contacts = []
        for (lvl, mn, nk), p in sorted(people.items(), key=lambda kv: -kv[1]["n"]):
            dr = dir_idx.get((lvl, mn, nk))
            row = dict(instrument=ins["instrument"], instrument_source=ins["source"], level=lvl, ministry=mn,
                       contact=dr.signatory if dr is not None else nk.title(), designation=p["desig"].most_common(1)[0][0],
                       evidence="signed documents", n_documents_signed=p["n"], last_signed=p["last"],
                       email=p["email"] or (getattr(dr, "roster_email", "") if dr is not None and isinstance(getattr(dr, "roster_email", ""), str) else ""),
                       phone=p["phone"],
                       roster_match=getattr(dr, "roster_match", "") if dr is not None and isinstance(getattr(dr, "roster_match", ""), str) else "",
                       roster_designation=getattr(dr, "roster_designation", "") if dr is not None and isinstance(getattr(dr, "roster_designation", ""), str) else "",
                       latest_posting=getattr(dr, "latest_posting", "") if dr is not None and isinstance(getattr(dr, "latest_posting", ""), str) else "",
                       latest_posting_date=getattr(dr, "latest_posting_date", "") if dr is not None and isinstance(getattr(dr, "latest_posting_date", ""), str) else "",
                       moved_since_signing=getattr(dr, "moved_since_signing", "") if dr is not None and isinstance(getattr(dr, "moved_since_signing", ""), str) else "",
                       document_urls=" ".join(doc_meta.loc[p["docs"][:5], "url"].tolist()))
            contacts.append(row)
        # roster officers whose division names the instrument (e.g. "PLI Cell", "Startup India")
        toks = [t for t in ins["key"].split() if len(t) > 3][:3]
        if toks and len(ministries):
            rr = rosters[rosters.ministry.isin(ministries.index[:2])]
            hit = rr[rr.div_key.apply(lambda dv: all(t in dv for t in toks[:2]))]
            for r in hit.head(5).itertuples():
                contacts.append(dict(instrument=ins["instrument"], instrument_source=ins["source"], level="centre", ministry=r.ministry,
                                     contact=r.name, designation=r.designation, evidence="roster division matches instrument", n_documents_signed=0,
                                     last_signed="", email=r.email if isinstance(r.email, str) else "", phone=r.phones if isinstance(r.phones, str) else "",
                                     roster_match=r.name, roster_designation=r.designation, latest_posting="", latest_posting_date="", moved_since_signing="",
                                     document_urls=""))
        contact_rows += contacts
        top = [c for c in contacts if c["evidence"] == "signed documents"][:3]
        index_rows.append(dict(instrument=ins["instrument"], instrument_source=ins["source"], level=level, ministry=ministries.index[0],
                               n_documents=len(ids), first_date=dm.date.dropna().astype(str).min() if dm.date.notna().any() else "",
                               last_date=dm.date.dropna().astype(str).max() if dm.date.notna().any() else "",
                               n_contacts=len([c for c in contacts if c["evidence"] == "signed documents"]),
                               top_contacts="; ".join(f"{c['contact']} ({c['designation']}{', ' + c['email'] if c['email'] else ''})" for c in top),
                               example_titles=" || ".join(dm.title.fillna("").astype(str).str[:90].head(3)), example_urls=" ".join(dm.url.head(3))))
    ci = pd.DataFrame(contact_rows); ii = pd.DataFrame(index_rows)
    ci.to_csv(REPO / "data/policy_contacts_from_documents.csv", index=False)
    ii.sort_values(["ministry", "n_documents"], ascending=[True, False]).to_csv(REPO / "data/policy_instruments_index.csv", index=False)
    write_report(ii, ci)
    print(f"linker: {len(ii)} instruments with documents ({(ii.instrument_source=='curated').sum()} curated), "
          f"{(ii.n_contacts>0).sum()} with at least one signing contact, {len(ci)} contact rows, {int((ci.email.astype(str).str.len()>0).sum())} with an email")


def write_report(ii, ci):
    L = []
    L.append("# Policy & incentive contacts — who signs the paperwork\n")
    L.append(f"_Built {time.strftime('%Y-%m-%d')} by `scripts/policy_contact_linker.py`. An instrument's contacts are the officials who signed its "
             f"notifications, guidelines, orders and clarifications (with any phone/email printed under the signature, the roster entry if matched, "
             f"and the latest posting known from the career tracker), plus roster officers whose division is named after the instrument._\n")
    L.append("| | Count |\n|---|---|")
    L.append(f"| Instruments with documents | {len(ii)} (curated {int((ii.instrument_source=='curated').sum())}, discovered from titles {int((ii.instrument_source=='documents').sum())}) |")
    L.append(f"| Instruments with at least one signing contact | {int((ii.n_contacts>0).sum())} |")
    L.append(f"| Contact rows | {len(ci)} ({int((ci.email.astype(str).str.len()>0).sum())} with email, {int((ci.phone.astype(str).str.len()>0).sum())} with phone) |")
    L.append(f"| Contacts flagged as moved since signing | {int((ci.moved_since_signing=='yes').sum())} |\n")
    L.append("## Curated incentive instruments (data/policy_windows.csv)\n")
    L.append("| Instrument | Ministry / level | Docs | Latest | Contacts (signed docs) |\n|---|---|---|---|---|")
    for r in ii[ii.instrument_source == "curated"].sort_values("n_documents", ascending=False).itertuples():
        L.append(f"| {r.instrument} | {r.ministry} ({r.level}) | {r.n_documents} | {r.last_date} | {r.top_contacts} |")
    L.append("\n## Instruments discovered from document titles, by ministry\n")
    for mn, g in ii[ii.instrument_source == "documents"].groupby("ministry"):
        g = g.sort_values("n_documents", ascending=False).head(25)
        L.append(f"### {mn}\n")
        L.append("| Instrument | Docs | Latest | Contacts (signed docs) |\n|---|---|---|---|")
        for r in g.itertuples():
            L.append(f"| {r.instrument} | {r.n_documents} | {r.last_date} | {r.top_contacts} |")
        L.append("")
    L.append("## Caveats\n")
    L.append("- 'Contact' = signed the instrument's paperwork; the signer of a notification is usually the Joint/Deputy/Under Secretary of the "
             "administering division, which is the right door to knock on, but not an officially published helpdesk.")
    L.append("- Instrument names discovered from titles are heuristic (Scheme / Yojana / Mission / Fund / PLI / Guidelines for …); near-duplicates are possible.")
    L.append("- `moved_since_signing = yes` comes from transfer news / ER sheets and is a lead to verify.")
    (REPO / "data/POLICY_CONTACTS.md").write_text("\n".join(L))


if __name__ == "__main__":
    main()
