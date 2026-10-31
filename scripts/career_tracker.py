#!/usr/bin/env python3
"""Where is this officer now? Career events (appointments, transfers, postings) from public sources, attached to the
signatories read from the order PDFs — because the person who signed a 2023 notification may hold another post today.

Sources (all read-only, robots-respecting, ~1 request/second per host, cached under data/career/articles/):
  sarkarimirror.com       WordPress JSON API (posts matching appointed / transferred / posted / reshuffle)
  whispersinthecorridors.in  news sitemap + /category/bureaucracy listing pages -> /news/<slug> articles
  psuwatch.com            daily sitemaps -> /bureaucracywatch/ and appointment-titled articles
  IAS civil list          data/ias_officers.csv current_posting + posting_wef (DoPT ER sheets) — authoritative for IAS

Stages:
  collect  -> data/career/articles/*.json         article title, date, text, source
  events   -> data/career/career_events.csv       one row per (person, new post, organisation, date, source, url)
                                                  regex on titles/first paragraph + Groq JSON extraction for multi-officer
                                                  reshuffle articles (cached in data/career/llm_cache.json)
  attach   -> data/signatories/signatory_directory.csv (+ data/states/signatory_directory_all_states.csv) gain
              latest_posting / latest_posting_date / latest_posting_source / moved_since_signing
           -> data/career/CAREER_TRACKER.md summary

Run:  /usr/bin/python3 scripts/career_tracker.py all [--days 540] [--max-articles 800]
"""
import argparse, csv, hashlib, json, os, re, sys, time
from datetime import datetime, timedelta
from pathlib import Path
from urllib.parse import urljoin, urlparse

import pandas as pd
import requests
from bs4 import BeautifulSoup

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))
import signatory_matrix as S  # noqa: E402  name_sim, norm_tokens, rank_of, clean_name
from state_pipeline import groq_json  # noqa: E402

CAREER = REPO / "data/career"
ART = CAREER / "articles"
ART.mkdir(parents=True, exist_ok=True)
UA = {"User-Agent": "Mozilla/5.0 (Macintosh) india-govt-yellow-pages career tracker; read-only, 1 req/s"}
KEY = re.compile(r"appoint|transfer|posted|posting|reshuffle|takes?[- ]charge|assume[sd]?[- ]charge|repatriat|deputation|"
                 r"empanel|new[- ](?:cmd|md|director|secretary|chairman|ceo|dg)|joint[- ]secretary|additional[- ]secretary|"
                 r"under[- ]secretary|deputy[- ]secretary|private[- ]secretary|\bias\b|\bips\b|\bifs\b|\birs\b|shuffl", re.I)
_last = {}


def get(url, timeout=30):
    host = urlparse(url).netloc
    dt = time.time() - _last.get(host, 0)
    if dt < 1.0:
        time.sleep(1.0 - dt)
    _last[host] = time.time()
    try:
        r = requests.get(url, headers=UA, timeout=timeout)
        if r.status_code == 200:
            return r
    except requests.RequestException:
        return None
    return None


def save_article(source, url, title, date, text, extra=None):
    aid = hashlib.sha1(url.encode()).hexdigest()[:16]
    p = ART / f"{aid}.json"
    if p.exists():
        return False
    p.write_text(json.dumps(dict(id=aid, source=source, url=url, title=title or "", date=date or "", text=text or "",
                                 **(extra or {})), ensure_ascii=False))
    return True


def have(url):
    return (ART / f"{hashlib.sha1(url.encode()).hexdigest()[:16]}.json").exists()


def article_html(url, source):
    r = get(url)
    if r is None:
        return False
    s = BeautifulSoup(r.text, "html.parser")
    h1 = s.find("h1")
    title = h1.get_text(" ", strip=True) if h1 else (s.title.get_text(strip=True) if s.title else "")
    date = ""
    m = s.find("meta", attrs={"property": "article:published_time"}) or s.find("meta", attrs={"name": "publish-date"})
    if m and m.get("content"):
        date = m["content"][:10]
    elif s.find("time") and (s.find("time").get("datetime") or s.find("time").get_text(strip=True)):
        date = (s.find("time").get("datetime") or s.find("time").get_text(strip=True))[:10]
    desc = s.find("meta", attrs={"name": "description"})
    art = s.find("article") or s
    paras = [p.get_text(" ", strip=True) for p in art.find_all("p") if len(p.get_text(strip=True)) > 40]
    text = "\n".join(paras[:12])
    if desc and desc.get("content") and desc["content"][:60] not in text:
        text = desc["content"] + "\n" + text
    return save_article(source, url, title, date, text)


# ------------------------------------------------------------------ collect
def collect_sarkarimirror(max_articles):
    base = "https://sarkarimirror.com/wp-json/wp/v2/posts"
    n = 0
    for term in ("appointed", "transferred", "posted", "reshuffle", "takes charge", "repatriated", "deputation"):
        for page in range(1, 40):
            r = get(f"{base}?per_page=100&page={page}&search={requests.utils.quote(term)}&_fields=date,link,title,content,excerpt")
            if r is None:
                break
            try:
                posts = r.json()
            except ValueError:
                break
            if not posts:
                break
            for p in posts:
                url = p["link"]
                if have(url):
                    continue
                html = (p.get("content") or {}).get("rendered") or (p.get("excerpt") or {}).get("rendered") or ""
                text = BeautifulSoup(html, "html.parser").get_text("\n", strip=True)
                title = BeautifulSoup((p.get("title") or {}).get("rendered") or "", "html.parser").get_text(strip=True)
                n += save_article("sarkarimirror", url, title, (p.get("date") or "")[:10], text[:4000])
            if len(posts) < 100 or n >= max_articles:
                break
        if n >= max_articles:
            break
    print(f"  sarkarimirror: {n} new articles")


def collect_whispers(max_articles, days):
    host = "https://whispersinthecorridors.in"
    urls = []
    r = get(f"{host}/sitemap-news.xml")
    if r is not None:
        urls += re.findall(r"<loc>([^<]+)</loc>", r.text)
    for cat in ("bureaucracy", "psu-watch", "archives", "corporate"):
        seen_page = 0
        for page in range(1, 40):
            for pat in (f"{host}/category/{cat}?page={page}", f"{host}/category/{cat}/page/{page}"):
                r = get(pat)
                if r is None:
                    continue
                links = [urljoin(host, a) for a in re.findall(r'href="(/news/[^"#?]+)', r.text)]
                new = [u for u in links if u not in urls]
                if new:
                    urls += new; seen_page = page
                    break
            else:
                break
            if page - seen_page > 1 or len(urls) > max_articles * 3:
                break
    urls = [u for u in dict.fromkeys(urls) if KEY.search(urlparse(u).path)]
    n = 0
    for u in urls:
        if have(u):
            continue
        n += bool(article_html(u, "whispersinthecorridors"))
        if n >= max_articles:
            break
    print(f"  whispersinthecorridors: {len(urls)} candidate urls, {n} new articles")


def collect_psuwatch(max_articles, days):
    host = "https://psuwatch.com"
    urls = []
    today = datetime.utcnow().date()
    for d in range(days):
        day = today - timedelta(days=d)
        r = get(f"{host}/sitemap/sitemap-daily-{day.isoformat()}.xml")
        if r is None:
            continue
        for u in re.findall(r"<loc>([^<]+)</loc>", r.text):
            path = urlparse(u).path
            if "/bureaucracywatch/" in path or KEY.search(path):
                urls.append(u)
        if len(urls) >= max_articles * 2:
            break
    urls = list(dict.fromkeys(urls))
    n = 0
    for u in urls:
        if have(u):
            continue
        n += bool(article_html(u, "psuwatch"))
        if n >= max_articles:
            break
    print(f"  psuwatch: {len(urls)} candidate urls, {n} new articles")


def collect(args):
    print("collect:")
    collect_sarkarimirror(args.max_articles)
    collect_psuwatch(args.max_articles, args.days)
    collect_whispers(args.max_articles, args.days)
    print(f"  articles on disk: {len(list(ART.glob('*.json')))}")


# ------------------------------------------------------------------ events
NAME = r"((?:(?:Dr|Shri|Smt|Ms|Mrs|Mr|Sh|Prof|Justice)\.?\s+)?[A-Z][A-Za-z.'\-]+(?:\s+[A-Z][A-Za-z.'\-]+){0,4})"
SVC = r"(?:\s*[,(]?\s*(IAS|IPS|IFS|IRS|IFoS|IRTS|IRAS|ICAS|IDAS|IPoS|IES|ISS|IDES|IRSME|IRSEE|IRSS|IRSE|IOFS|ITS|CSS)\s*(?:\(([A-Z]{2,3})[:\s-]*(\d{4})\))?\)?)?"
VERB = r"(?:has been|have been|is|was|been)?\s*(appointed|posted|transferred|repatriated|empanelled|designated|redesignated|promoted|given (?:the )?additional charge|takes? (?:over )?(?:the )?charge|assumes? (?:the )?charge|joins|named|selected|elevated|relieved)"
POST = r"(?:\s+(?:as|to|of|for|in)\s+(?:the\s+)?(?:post of\s+|new\s+)?)([A-Z][^.;,\n]{3,80}?)"
ORG = r"(?:\s*(?:,|in|of|at|to|with)\s+(?:the\s+)?([A-Z][^.;\n]{3,100}?))?"
EVENT = re.compile(NAME + SVC + r"[,\s]*" + VERB + POST + ORG + r"(?=[.;,\n]|$)")
STOP_PERSON = re.compile(r"\b(?:government|ministry|department|cabinet|committee|board|commission|authority|court|bank|limited|ltd|india|"
                         r"state|union|central|new delhi|officers?|judges?|advocates?|posts?|order|notification|the|a|an|many|as|several|"
                         r"these|those|following|there|here|press|news|update|watch|whispers|corridors|mirror|sarkari)\b", re.I)


def regex_events(a):
    out = []
    blobs = [a.get("title", "")] + [x for x in (a.get("text") or "").split("\n")[:4]]
    for src_i, blob in enumerate(blobs):
        for m in EVENT.finditer(blob or ""):
            name = S.clean_name(m.group(1))
            if len(name.split()) < 2 or STOP_PERSON.search(name) or S.all_dictionary_words(name):
                continue
            out.append(dict(name=name, service=m.group(2) or "", cadre=m.group(3) or "", batch=m.group(4) or "",
                            event=m.group(5).lower(), new_post=(m.group(6) or "").strip(" ,"), new_org=(m.group(7) or "").strip(" ,"),
                            event_date=a.get("date", ""), source=a["source"], url=a["url"], snippet=blob[:300],
                            method="regex-title" if src_i == 0 else "regex-body"))
    return out


LLM_CACHE = CAREER / "llm_cache.json"
MULTI = re.compile(r"\b(\d{1,3}|several|many)\s+(?:ias|ips|ifs|irs|officers?|dcs?|acs?|secretaries|collectors|sps?)\b.*?(?:transferred|reshuffle|posted|appointed|shuffl)|reshuffle|transferred|transfers", re.I)


def llm_events(a, cache):
    if a["id"] in cache:
        return cache[a["id"]]
    text = (a.get("title", "") + "\n" + (a.get("text") or ""))[:6000]
    res = groq_json(
        "Extract every personnel movement in this Indian bureaucracy news item. Return JSON only: "
        '{"events": [{"name": "<person, honorifics removed>", "service": "<IAS/IPS/IFS/IRS/PCS/other or empty>", "batch": "<cadre:year or empty>", '
        '"event": "<appointed|transferred|posted|promoted|additional charge|repatriated|relieved|retired|other>", '
        '"new_post": "<designation>", "new_org": "<organisation / department / place>", "previous_post": "<if stated>"}]}. '
        "Only people explicitly named with a new post; no speculation.", text)
    ev = (res or {}).get("events") or []
    rows = []
    for e in ev:
        if not isinstance(e, dict) or not e.get("name"):
            continue
        nm = S.clean_name(str(e["name"]))
        if len(nm.split()) < 2 or STOP_PERSON.search(nm):
            continue
        rows.append(dict(name=nm, service=str(e.get("service") or ""), cadre="", batch=str(e.get("batch") or ""),
                         event=str(e.get("event") or "").lower(), new_post=str(e.get("new_post") or ""), new_org=str(e.get("new_org") or ""),
                         event_date=a.get("date", ""), source=a["source"], url=a["url"], snippet=str(e.get("previous_post") or "")[:200], method="llm"))
    cache[a["id"]] = rows
    LLM_CACHE.write_text(json.dumps(cache, ensure_ascii=False))
    time.sleep(2.5)
    return rows


def events(args):
    arts = [json.loads(p.read_text()) for p in sorted(ART.glob("*.json"))]
    cache = json.loads(LLM_CACHE.read_text()) if LLM_CACHE.exists() else {}
    rows, llm_n = [], 0
    for a in arts:
        got = regex_events(a)
        multi = bool(MULTI.search(a.get("title", ""))) or len(got) == 0 and KEY.search(a.get("title", "") or "")
        if (multi or len(got) == 0) and llm_n < args.max_llm and os.environ.get("CAREER_NO_LLM") != "1":
            if a["id"] not in cache:
                llm_n += 1
            got += llm_events(a, cache)
        rows += got
    # IAS ER sheets: authoritative current posting
    p = REPO / "data/ias_officers.csv"
    if p.exists():
        ias = pd.read_csv(p, low_memory=False)
        for r in ias.itertuples():
            post = str(getattr(r, "current_posting", "") or "")
            if not post or post == "nan":
                continue
            wef = str(getattr(r, "posting_wef", "") or "")
            d = ""
            m = re.match(r"(\d{2})/(\d{2})/(\d{4})", wef)
            if m:
                d = f"{m.group(3)}-{m.group(2)}-{m.group(1)}"
            rows.append(dict(name=S.clean_name(str(r.name_en)), service="IAS", cadre=str(getattr(r, "cadre_code", "") or ""),
                             batch=str(getattr(r, "allotment_year", "") or ""), event="current posting (ER sheet)",
                             new_post=post.split(",")[0].strip(), new_org=post, event_date=d, source="dopt_er_sheet",
                             url=str(getattr(r, "er_sheet_url", "") or ""), snippet="", method="civil-list"))
    df = pd.DataFrame(rows)
    if df.empty:
        print("events: none"); return
    df["name_key"] = df.name.map(lambda x: " ".join(S.norm_tokens(x)))
    df = df[df.name_key.str.len() >= 5].drop_duplicates(["name_key", "new_post", "new_org", "url"])
    df.to_csv(CAREER / "career_events.csv", index=False)
    print(f"events: {len(df)} rows ({df.source.value_counts().to_dict()}); LLM calls this run: {llm_n}")


# ------------------------------------------------------------------ attach
def attach_to(directory_path, ev, state_mode=False):
    if not directory_path.exists():
        return None
    d = pd.read_csv(directory_path)
    if d.empty:
        return d
    idx = {}
    for i, r in ev.iterrows():
        for t in set(S.norm_tokens(r["name"])):
            if len(t) > 2:
                idx.setdefault(t, []).append(i)
    cols = {k: [] for k in ("latest_posting", "latest_posting_org", "latest_posting_date", "latest_posting_source", "latest_posting_url",
                            "posting_match_confidence", "moved_since_signing", "career_events_n")}
    for r in d.itertuples():
        toks = S.norm_tokens(str(r.signatory))
        pool = set()
        for t in toks:
            if len(t) > 2:
                pool.update(idx.get(t, []))
        best = []
        rs = S.rank_of(str(r.designations).split("|")[0]) if isinstance(r.designations, str) else None
        for i in pool:
            e = ev.loc[i]
            sc = S.name_sim(str(r.signatory), e["name"])
            if sc < 0.85:
                continue
            re_ = S.rank_of(e["new_post"])
            if rs is not None and re_ is not None and abs(rs - re_) >= 3:
                continue   # an Under Secretary does not become Chief Secretary in one move
            ntok = len(toks)
            conf = "high" if (sc >= 0.95 and (ntok >= 3 or e["source"] == "dopt_er_sheet" and re_ is not None and rs is not None and abs(rs - re_) <= 1)) \
                else "medium" if sc >= 0.95 else "low"
            best.append((e["event_date"] or "", sc, conf, i))
        if not best:
            for k in cols:
                cols[k].append("" if k != "career_events_n" else 0)
            continue
        best.sort(reverse=True)
        date, sc, conf, i = best[0]
        e = ev.loc[i]
        cols["latest_posting"].append(e["new_post"]); cols["latest_posting_org"].append(e["new_org"])
        cols["latest_posting_date"].append(e["event_date"]); cols["latest_posting_source"].append(e["source"])
        cols["latest_posting_url"].append(e["url"]); cols["posting_match_confidence"].append(conf)
        last_signed = str(getattr(r, "last_date", "") or "")
        moved = bool(e["event_date"]) and bool(last_signed) and last_signed != "nan" and e["event_date"][:7] > last_signed[:7] \
            and not (set(S.norm_tokens(str(r.ministry))) & set(S.norm_tokens(str(e["new_org"]))))
        cols["moved_since_signing"].append("yes" if moved else ("same org / older" if e["event_date"] else "undated"))
        cols["career_events_n"].append(len(best))
    for k, v in cols.items():
        d[k] = v
    d.to_csv(directory_path, index=False)
    return d


def attach(args):
    ev = pd.read_csv(CAREER / "career_events.csv")
    ev = ev[ev.event_date.notna() | (ev.source == "dopt_er_sheet")].fillna("")
    out = []
    c = attach_to(REPO / "data/signatories/signatory_directory.csv", ev)
    if c is not None:
        out.append(("centre", c))
    s = attach_to(REPO / "data/states/signatory_directory_all_states.csv", ev, state_mode=True)
    if s is not None:
        out.append(("states", s))
    lines = ["# Career tracker — where are the signatories now?\n",
             f"_Built {time.strftime('%Y-%m-%d')} by `scripts/career_tracker.py`. Events: {len(ev)} "
             f"({ev.source.value_counts().to_dict()}); articles cached: {len(list(ART.glob('*.json')))}._\n",
             "| Directory | signers | with a later/current posting found | moved since they signed | high confidence |", "|---|---|---|---|---|"]
    for name, d in out:
        has = d.latest_posting.astype(str).str.len() > 0
        lines.append(f"| {name} | {len(d)} | {int(has.sum())} | {int((d.moved_since_signing == 'yes').sum())} | {int((d.posting_match_confidence == 'high').sum())} |")
    lines.append("\n## Signers who have moved (sample, high/medium confidence)\n")
    lines.append("| Directory | Signatory | Signed as (ministry) | Last signed | Now | Since | Source |\n|---|---|---|---|---|---|---|")
    for name, d in out:
        mv = d[(d.moved_since_signing == "yes") & d.posting_match_confidence.isin(["high", "medium"])].sort_values("n_documents", ascending=False).head(40)
        for r in mv.itertuples():
            lines.append(f"| {name} | {r.signatory} | {str(r.designations).split('|')[0].strip()} ({r.ministry}) | {r.last_date} | "
                         f"{r.latest_posting} — {str(r.latest_posting_org)[:70]} | {r.latest_posting_date} | [{r.latest_posting_source}]({r.latest_posting_url}) |")
    lines.append("\n_Name matches on two-token common names are marked `low`/`medium`; treat `moved_since_signing=yes` as a lead to verify, not a fact._\n")
    (CAREER / "CAREER_TRACKER.md").write_text("\n".join(lines))
    print("\n".join(lines[:8]))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("stages", nargs="+")
    ap.add_argument("--days", type=int, default=540)
    ap.add_argument("--max-articles", type=int, default=800)
    ap.add_argument("--max-llm", type=int, default=250)
    a = ap.parse_args()
    for st in (["collect", "events", "attach"] if a.stages == ["all"] else a.stages):
        globals()[st](a)
