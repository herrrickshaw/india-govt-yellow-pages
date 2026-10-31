#!/usr/bin/env python3
"""What new policies / incentives were announced, and who signs for them?

Sources
  * PIB press releases — the SQLite index kept by india-trade-sector-policy-recommendations/scripts/pib_index.py
    (`--update` refreshes it day by day; the ASP.NET traps are solved there), filtered by date and policy keywords,
    detail text read from the release page (one request/second, cached under data/new_policies/pib/).
  * Ministry websites — ministry_documents/data/all_documents.csv.gz rows dated in the window whose title / category
    says scheme, guideline, incentive, PLI, subsidy, policy, notification, amendment…, plus the subject lines already
    extracted from their PDFs (data/signatories/signatures.csv).

Each shortlisted item is classified with Groq (JSON): is it a policy / incentive instrument, its name, type
(scheme / PLI / subsidy / policy / guidelines / amendment / extension / tariff-duty / other), status
(approved / launched / notified / draft / extended / amended / update), beneficiaries, outlay, dates.  Known
instruments (data/policy_windows.csv, data/policy_instruments_index.csv) are marked; signing contacts come from
data/policy_contacts_from_documents.csv, else the ministry's most active signers in data/signatories/signatory_directory.csv,
else the PIB ministry contact (data/pib_ministry_contacts.csv).

Outputs
  data/new_policies_incentives.csv, data/NEW_POLICIES.md
  data/discovered_instruments.csv  (feeds scripts/policy_contact_linker.py as an extra instrument source)

Run:  /usr/bin/python3 scripts/new_policy_scanner.py [--days 120] [--max-llm 150] [--pib-db <path>]
"""
import argparse, hashlib, json, re, sqlite3, sys, time
from datetime import date, timedelta
from pathlib import Path

import pandas as pd
import requests
from bs4 import BeautifulSoup

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))
import signatory_matrix as S  # noqa: E402
from state_pipeline import groq_json  # noqa: E402

OUT = REPO / "data/new_policies"; (OUT / "pib").mkdir(parents=True, exist_ok=True)
PIB_DB_DEFAULT = Path.home() / "india-trade-sector-policy-recommendations/data/pib_index.sqlite"
KEY = re.compile(r"scheme|incentive|subsid|\bpli\b|production[- ]linked|yojana|mission|policy|guideline|notif|amend|cabinet approves|"
                 r"approves|launch|viability gap|interest subvention|rebate|concession|exemption|tariff|duty|fund\b|package|"
                 r"relief|grant|credit guarantee|loan|interest-free|extension of|extended|deadline|last date|window|portal|"
                 r"empanel|registration open|applications? invited|eoi|expression of interest|rfp|bid", re.I)
NOISE = re.compile(r"congratulat|condol|birth anniversary|greets|pays tribute|visit of|visits|meets|meeting with|inaugurat|"
                   r"felicitat|celebrat|webinar|yoga|cleanliness|swachhata pakhwada|hindi diwas|rajbhasha|vigilance awareness|"
                   r"sports|medal|cricket|film festival|exhibition|fair|mela|interview|article by|opinion|feature|backgrounder|"
                   r"quiz|essay|painting|photo|gallery|press conference|press tour|tour of|curtain raiser|factsheet|fact sheet",
                   re.I)
UA = {"User-Agent": "Mozilla/5.0 (Macintosh) india-govt-yellow-pages new-policy scanner; read-only, 1 req/s"}
_last = [0.0]


def pib_text(url):
    aid = hashlib.sha1(url.encode()).hexdigest()[:16]
    p = OUT / "pib" / f"{aid}.txt"
    if p.exists():
        return p.read_text()
    u = url.replace("https://pib.gov.in", "https://www.pib.gov.in")
    if "lang=" not in u:
        u += ("&" if "?" in u else "?") + "reg=3&lang=1"
    dt = time.time() - _last[0]
    if dt < 1.0:
        time.sleep(1.0 - dt)
    _last[0] = time.time()
    try:
        r = requests.get(u, headers=UA, timeout=30)
    except requests.RequestException:
        return ""
    if r.status_code != 200:
        return ""
    s = BeautifulSoup(r.text, "html.parser")
    body = s.select_one("div.innner-page-main-about-us-content-right-part") or s.select_one("#PdfDiv") or s
    text = re.sub(r"\s+", " ", body.get_text(" ", strip=True))[:6000]
    p.write_text(text)
    return text


def shortlist_pib(db, since):
    con = sqlite3.connect(str(db))
    rows = con.execute("select date, ministry, title, url from pib_items where kind='release' and date>=? order by date desc", (since,)).fetchall()
    con.close()
    out = []
    for d, m, t, u in rows:
        t = re.sub(r"\s+", " ", str(t or "")); m = re.sub(r"\s+", " ", str(m or ""))
        if KEY.search(t) and not NOISE.search(t):
            out.append(dict(source="PIB", date=d, ministry=m, title=t, url=u, subject=""))
    return pd.DataFrame(out)


def shortlist_ministry(since):
    d = pd.read_csv(REPO / "ministry_documents/data/all_documents.csv.gz", compression="gzip", low_memory=False)
    d["dt"] = pd.to_datetime(d.date, errors="coerce")
    d = d[d.dt >= pd.Timestamp(since)]
    blob = d.title.fillna("") + " " + d.category.fillna("") + " " + d.group.fillna("")
    d = d[blob.str.contains(KEY) & ~d.title.fillna("").str.contains(NOISE)]
    subj = {}
    sp = REPO / "data/signatories/signatures.csv"
    if sp.exists():
        sg = pd.read_csv(sp).drop_duplicates("doc_id")
        subj = dict(zip(sg.doc_id, sg.subject.fillna("")))
    rows = []
    for r in d.itertuples():
        rows.append(dict(source="ministry site", date=str(r.date), ministry=r.ministry, title=re.sub(r"\s+", " ", str(r.title)),
                         url=r.url, subject=subj.get(S.doc_id(str(r.url)), "")))
    return pd.DataFrame(rows)


CLASSIFY_SYS = (
    "You classify Indian government press releases and documents. For each item decide whether it announces, notifies, "
    "amends, extends or opens applications for a POLICY or INCENTIVE INSTRUMENT (a scheme, PLI, subsidy, grant, fund, "
    "tax/duty concession, policy, guidelines, tender/EoI under a scheme). Return JSON only: "
    '{"items": [{"i": <index>, "is_instrument": true|false, "instrument": "<canonical short name or empty>", '
    '"type": "scheme|PLI|subsidy|grant-fund|tax-duty|policy|guidelines|amendment|extension|tender-eoi|other", '
    '"status": "approved|launched|notified|draft|extended|amended|applications-open|update|other", '
    '"new_or_update": "new|update|unclear", "beneficiaries": "<who can avail, short>", "summary": "<one sentence>"}]}. '
    "Mark reports of past achievements, statistics, events or ceremonies as is_instrument=false."
)


def classify(df, cache, max_llm):
    df = df.copy()
    df["key"] = df.url.map(lambda u: hashlib.sha1(str(u).encode()).hexdigest()[:16])
    todo = df[~df.key.isin(cache)]
    calls = 0
    for i in range(0, len(todo), 10):
        if calls >= max_llm:
            break
        chunk = todo.iloc[i:i + 10]
        items = [{"i": k, "source": r.source, "date": r.date, "ministry": r.ministry, "title": r.title, "subject": (r.subject or "")[:200]}
                 for k, r in enumerate(chunk.itertuples())]
        res = groq_json(CLASSIFY_SYS, json.dumps({"items": items}, ensure_ascii=False)); calls += 1
        got = {x.get("i"): x for x in (res or {}).get("items", []) if isinstance(x, dict)}
        for k, r in enumerate(chunk.itertuples()):
            cache[r.key] = got.get(k, {"is_instrument": None})
        (OUT / "classify_cache.json").write_text(json.dumps(cache, ensure_ascii=False))
        time.sleep(2.5)
    for c in ("is_instrument", "instrument", "type", "status", "new_or_update", "beneficiaries", "summary"):
        df[c] = df.key.map(lambda k: (cache.get(k) or {}).get(c))
    return df, calls


DETAIL_SYS = ("From this Indian government press release text, extract the instrument details. JSON only: "
              '{"instrument": "<name>", "outlay": "<amount or empty>", "period": "<validity / dates or empty>", '
              '"eligibility": "<short>", "how_to_apply": "<portal / nodal agency / deadline or empty>", "nodal_body": "<ministry or agency>"}')


def enrich_pib(df, cache, max_llm):
    df = df.copy()
    for c in ("outlay", "period", "eligibility", "how_to_apply", "nodal_body"):
        df[c] = ""
    calls = 0
    for idx, r in df[(df.source == "PIB") & (df.is_instrument == True)].iterrows():  # noqa: E712
        ck = "detail:" + r.key
        if ck not in cache:
            if calls >= max_llm:
                continue
            text = pib_text(r.url)
            if len(text) < 200:
                cache[ck] = {}
            else:
                cache[ck] = groq_json(DETAIL_SYS, text[:5000]) or {}
                calls += 1; time.sleep(2.5)
            (OUT / "classify_cache.json").write_text(json.dumps(cache, ensure_ascii=False))
        for c in ("outlay", "period", "eligibility", "how_to_apply", "nodal_body"):
            df.at[idx, c] = (cache[ck] or {}).get(c, "") or ""
    return df, calls


def instr_key(name):
    stop = {"the", "and", "for", "of", "in", "on", "to", "under", "scheme", "schemes", "guidelines", "policy", "rules", "new", "india",
            "indian", "national", "central", "government", "ministry", "department", "programme", "program", "yojana", "mission"}
    return " ".join(t for t in re.split(r"[^a-z0-9]+", str(name).lower()) if t and t not in stop and len(t) > 2)


def attach_known_and_contacts(df):
    known_cur = {}
    for fn in ("policy_windows.csv", "policy_contacts.csv"):
        p = REPO / "data" / fn
        if p.exists():
            for ins in pd.read_csv(p, on_bad_lines="skip").instrument.dropna().unique():
                known_cur[instr_key(re.sub(r"\(.*?\)", "", ins))] = ins
    idx_p = REPO / "data/policy_instruments_index.csv"
    known_docs = {}
    if idx_p.exists():
        for r in pd.read_csv(idx_p).itertuples():
            known_docs[instr_key(r.instrument)] = r
    contacts_p = REPO / "data/policy_contacts_from_documents.csv"
    cdf = pd.read_csv(contacts_p) if contacts_p.exists() else pd.DataFrame()
    if len(cdf):
        cdf["ikey"] = cdf.instrument.map(instr_key)
    direc_p = REPO / "data/signatories/signatory_directory.csv"
    direc = pd.read_csv(direc_p) if direc_p.exists() else pd.DataFrame()
    pibc_p = REPO / "data/pib_ministry_contacts.csv"
    pibc = pd.read_csv(pibc_p) if pibc_p.exists() else pd.DataFrame()

    def mkey(m):
        return {t for t in re.split(r"[^a-z]+", str(m).lower()) if len(t) > 4 and t not in ("ministry", "department", "affairs", "government")}

    rows = []
    for r in df.itertuples():
        k = instr_key(r.instrument or r.title)
        toks = set(k.split())
        kc = next((v for kk, v in known_cur.items() if kk and (kk == k or (len(set(kk.split()) & toks) >= 2))), "")
        kd = next((v for kk, v in known_docs.items() if kk and (kk == k or (len(set(kk.split()) & toks) >= 2))), None)
        contacts, evidence = "", ""
        if len(cdf) and kd is not None:
            c = cdf[(cdf.ikey == instr_key(kd.instrument)) & (cdf.evidence == "signed documents")].head(3)
            contacts = "; ".join(f"{x.contact} ({x.designation}{', ' + str(x.email) if isinstance(x.email, str) and x.email else ''})" for x in c.itertuples())
            evidence = "signed this instrument's documents" if contacts else ""
        if not contacts and len(direc):
            mk = mkey(r.ministry)
            dm = direc[direc.ministry.map(lambda m: bool(mk & mkey(m)))]
            dm = dm[dm.designations.fillna("").str.contains(r"Secretary|Director|Scientist|Commissioner", case=False)].sort_values("n_documents", ascending=False).head(3)
            contacts = "; ".join(f"{x.signatory} ({str(x.designations).split('|')[0].strip()}{', ' + str(x.email) if isinstance(x.email, str) and x.email else ''})" for x in dm.itertuples())
            evidence = "most active signers in this ministry" if contacts else ""
        if not contacts and len(pibc):
            mk = mkey(r.ministry)
            pm = pibc[pibc.ministry.map(lambda m: bool(mk & mkey(m))) & pibc.contact_name.notna()].head(2)
            contacts = "; ".join(f"{x.contact_name} ({x.designation}{', ' + str(x.email) if isinstance(x.email, str) and x.email else ''})" for x in pm.itertuples())
            evidence = "igod minister/secretary contact" if contacts else ""
        rows.append(dict(known_curated_instrument=kc, seen_in_document_index=(kd.instrument if kd is not None else ""),
                         docs_in_index=(int(kd.n_documents) if kd is not None else 0), contacts=contacts, contact_evidence=evidence))
    return pd.concat([df.reset_index(drop=True), pd.DataFrame(rows)], axis=1)


def write_report(df, since):
    L = [f"# New policies & incentives since {since} — PIB and ministry websites\n",
         f"_Built {time.strftime('%Y-%m-%d')} by `scripts/new_policy_scanner.py`. Shortlisted {len(df)} items by keyword, "
         f"{int((df.is_instrument == True).sum())} classified as policy/incentive instruments. 'Contacts' are the officials who signed "
         f"the instrument's documents, else the ministry's most active signers, else the igod minister/secretary contact._\n"]  # noqa: E712
    ins = df[df.is_instrument == True].copy()  # noqa: E712
    L.append("| | Count |\n|---|---|")
    L.append(f"| Instruments: new | {int((ins.new_or_update == 'new').sum())} |")
    L.append(f"| Instruments: updates / amendments / extensions | {int((ins.new_or_update != 'new').sum())} |")
    L.append(f"| Already in the curated incentive list | {int((ins.known_curated_instrument != '').sum())} |")
    L.append(f"| Already seen in the ministry document index (with signers) | {int((ins.docs_in_index > 0).sum())} |")
    L.append(f"| With a named contact | {int((ins.contacts != '').sum())} |\n")
    L.append("## Newly announced instruments (newest first)\n")
    L.append("| Date | Ministry | Instrument | Type / status | Summary | Outlay / period | Contacts | Source |\n|---|---|---|---|---|---|---|---|")
    for r in ins[ins.new_or_update == "new"].sort_values("date", ascending=False).itertuples():
        L.append(f"| {r.date} | {r.ministry} | **{r.instrument}** | {r.type} / {r.status} | {str(r.summary)[:160]} | {r.outlay} {r.period} | {r.contacts} | [{r.source}]({r.url}) |")
    L.append("\n## Updates, amendments, extensions, application windows\n")
    L.append("| Date | Ministry | Instrument | Type / status | Summary | Contacts | Source |\n|---|---|---|---|---|---|---|")
    for r in ins[ins.new_or_update != "new"].sort_values("date", ascending=False).head(150).itertuples():
        L.append(f"| {r.date} | {r.ministry} | {r.instrument} | {r.type} / {r.status} | {str(r.summary)[:140]} | {r.contacts} | [{r.source}]({r.url}) |")
    L.append("\n_Classification is by LLM over titles (and release text for PIB items); verify before acting. Re-run with "
             "`--days N` for a longer window; PIB index refresh: `python3 scripts/pib_index.py --update` in india-trade-sector-policy-recommendations._\n")
    (REPO / "data/NEW_POLICIES.md").write_text("\n".join(L))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--days", type=int, default=120)
    ap.add_argument("--max-llm", type=int, default=150)
    ap.add_argument("--pib-db", default=str(PIB_DB_DEFAULT))
    a = ap.parse_args()
    since = (date.today() - timedelta(days=a.days)).isoformat()
    parts = []
    if Path(a.pib_db).exists():
        parts.append(shortlist_pib(a.pib_db, since))
    parts.append(shortlist_ministry(since))
    df = pd.concat([p for p in parts if len(p)], ignore_index=True).drop_duplicates("url")
    print(f"shortlist: {len(df)} items since {since} ({df.source.value_counts().to_dict()})")
    cache_p = OUT / "classify_cache.json"
    cache = json.loads(cache_p.read_text()) if cache_p.exists() else {}
    df, n1 = classify(df, cache, a.max_llm)
    df, n2 = enrich_pib(df, cache, a.max_llm)
    df = attach_known_and_contacts(df)
    df = df.sort_values(["is_instrument", "date"], ascending=[False, False])
    df.drop(columns=["key"]).to_csv(REPO / "data/new_policies_incentives.csv", index=False)
    ins = df[df.is_instrument == True]  # noqa: E712
    disc = ins[["instrument", "ministry", "type", "status", "new_or_update", "date", "url", "source"]].dropna(subset=["instrument"])
    disc = disc[disc.instrument.astype(str).str.len() > 3].drop_duplicates("instrument")
    disc.to_csv(REPO / "data/discovered_instruments.csv", index=False)
    write_report(df, since)
    print(f"classified: {int((df.is_instrument == True).sum())} instruments ({int((ins.new_or_update == 'new').sum())} new); "  # noqa: E712
          f"LLM calls {n1 + n2}; with contacts {int((ins.contacts != '').sum())}; discovered_instruments.csv {len(disc)} rows")


if __name__ == "__main__":
    main()
