#!/usr/bin/env python3
"""Who signed which order / notification, and for which topic is each officer the contact.

Links the officers in the who's-who rosters (data/ministry_officials.csv, data/officials.csv,
data/ias_officers.csv, data/ips_officers.csv) to the orders, notifications, circulars, OMs and gazette
notifications indexed in ministry_documents/data/all_documents.csv.gz, by reading the signature block
at the end of each PDF.

Stages (each writes under data/signatories/):
  select   -> candidates.csv          orders/notifications/… PDFs for ministries that have an officer roster
  fetch    -> pdf/<doc_id>.pdf        polite download (1 req/s per host, parallel across hosts; gitignored)
  extract  -> signatures.csv          signatory name + designation + subject per PDF (pdftotext)
  match    -> notification_signatories.csv   signatory -> roster officer (name similarity, same ministry first)
  matrix   -> officer_topic_matrix.csv, officer_topic_pivot.csv, SIGNATORY_MATRIX.md

Run:  /usr/bin/python3 scripts/signatory_matrix.py all      (or one stage name)
"""
import csv, hashlib, json, os, re, subprocess, sys, time, unicodedata
from collections import defaultdict, Counter
from concurrent.futures import ThreadPoolExecutor
from difflib import SequenceMatcher
from pathlib import Path
from urllib.parse import urlparse

import pandas as pd

REPO = Path(__file__).resolve().parent.parent
DOCS = REPO / "ministry_documents/data/all_documents.csv.gz"
OUT = REPO / "data/signatories"
PDF = OUT / "pdf"
OUT.mkdir(parents=True, exist_ok=True); PDF.mkdir(exist_ok=True)

DOC_PAT = re.compile(r"order|notification|gazette|circular|memorand|\bo\.?m\b|guideline|policy|rules|amendment|"
                     r"g\.s\.r|s\.o\.|advisory|instruction|direction|sanction|appoint|transfer|posting|tender|corrigend", re.I)
MAX_BYTES = 25_000_000
OCR_LANG = "eng"            # state_pipeline.py sets e.g. "hin+eng" per state
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) india-govt-yellow-pages signatory index; read-only"


def doc_id(url: str) -> str:
    return hashlib.sha1(url.encode()).hexdigest()[:16]


# ---------------------------------------------------------------- select
ALL_MINISTRIES = os.environ.get("SIG_ALL_MINISTRIES") == "1"      # every ministry, matched against civil lists + igod
PER_MINISTRY_CAP = int(os.environ.get("SIG_PER_MINISTRY_CAP", "0"))  # 0 = no cap; newest documents first


def select():
    d = pd.read_csv(DOCS, compression="gzip", low_memory=False)
    rosters = pd.read_csv(REPO / "data/ministry_officials.csv")
    mins = set(rosters.ministry.unique())
    dd = d.copy() if ALL_MINISTRIES else d[d.ministry.isin(mins)].copy()
    txt = (dd.title.fillna("") + " " + dd.group.fillna("") + " " + dd.category.fillna(""))
    cand = dd[txt.str.contains(DOC_PAT) & dd.url.fillna("").str.lower().str.contains(r"\.pdf")].copy()
    cand = cand.drop_duplicates("url")
    if PER_MINISTRY_CAP:
        cand = cand.sort_values("date", ascending=False, na_position="last")
        # ministries with a full roster keep everything; the rest are capped (newest first)
        cand = pd.concat([cand[cand.ministry.isin(mins)], cand[~cand.ministry.isin(mins)].groupby("ministry", group_keys=False).head(PER_MINISTRY_CAP)])
    # policy / incentive documents first, so a partial fetch is already useful for the contact map
    POLICY = re.compile(r"scheme|guideline|incentive|subsid|\bpli\b|production linked|yojana|mission|notification|gazette|g\.s\.r|s\.o\.|"
                        r"amendment|policy|tariff|duty|exemption|viability gap|interest subvention|grant|fund|\bsop\b|eligib|"
                        r"application|empanel|approval|clarification|faq|extension of (?:date|timeline|deadline)", re.I)
    cand["_prio"] = (~(cand.title.fillna("") + " " + cand.group.fillna("") + " " + cand.category.fillna("")).str.contains(POLICY)).astype(int)
    cand = cand.sort_values(["_prio", "date"], ascending=[True, False], na_position="last").drop(columns="_prio")
    prev = OUT / "candidates.csv"
    if prev.exists():   # keep earlier selections (their PDFs and text are cached)
        old = pd.read_csv(prev)
        cand = pd.concat([old.drop(columns=[c for c in ("doc_id", "host") if c in old.columns]), cand]).drop_duplicates("url")
    cand.insert(0, "doc_id", cand.url.map(doc_id))
    cand["host"] = cand.url.map(lambda u: urlparse(u).netloc)
    cand = cand.drop(columns=[c for c in ("source", "slug", "language", "size") if c in cand.columns])  # 'api,<title>' trips gitleaks
    cand.to_csv(OUT / "candidates.csv", index=False)
    print(f"select: {len(cand)} candidate PDFs across {cand.ministry.nunique()} ministries, {cand.host.nunique()} hosts")


# ---------------------------------------------------------------- fetch
def _curl(url, dest):
    tmp = dest.with_suffix(".part")
    cmd = ["curl", "-sSL", "--max-time", "120", "--max-filesize", str(MAX_BYTES), "-A", UA,
           "-o", str(tmp), "-w", "%{http_code} %{content_type}", url]
    r = subprocess.run(cmd, capture_output=True, text=True)
    code, _, ctype = r.stdout.partition(" ")
    ok = code == "200" and tmp.exists() and tmp.stat().st_size > 0
    if ok:
        with open(tmp, "rb") as f:
            head = f.read(5)
        ok = head.startswith(b"%PDF")
    if ok:
        tmp.rename(dest)
    else:
        tmp.unlink(missing_ok=True)
    return code, ctype.strip(), ok, (r.stderr or "").strip()[:200]


def fetch():
    cand = pd.read_csv(OUT / "candidates.csv")
    log_path = OUT / "fetch_log.csv"
    done = set()
    if log_path.exists():
        done = set(pd.read_csv(log_path).doc_id)
    by_host = defaultdict(list)
    for r in cand.itertuples():
        if r.doc_id in done or (PDF / f"{r.doc_id}.pdf").exists():
            continue
        by_host[r.host].append((r.doc_id, r.url))
    print(f"fetch: {sum(map(len, by_host.values()))} to download over {len(by_host)} hosts")
    new = log_path.exists() is False
    lf = open(log_path, "a", newline=""); w = csv.writer(lf)
    if new:
        w.writerow(["doc_id", "url", "http", "content_type", "ok", "err", "ts"])

    def worker(job):
        host, items = job
        n = 0
        for did, url in items:
            t0 = time.time()
            try:
                code, ctype, ok, err = _curl(url, PDF / f"{did}.pdf")
            except Exception as e:  # noqa
                code, ctype, ok, err = "exc", "", False, str(e)[:200]
            w.writerow([did, url, code, ctype, int(ok), err, int(time.time())]); lf.flush()
            n += ok
            time.sleep(max(0, 1.0 - (time.time() - t0)))  # never more than ~1 request/second per worker
        return host, n

    # hosts that answer slowly (~10 s/file) get two workers; that is still well under 1 request/second
    jobs = []
    for host, items in by_host.items():
        if len(items) > 100:
            jobs += [(host, items[0::2]), (host, items[1::2])]
        else:
            jobs.append((host, items))
    with ThreadPoolExecutor(max_workers=min(12, len(jobs) or 1)) as ex:
        for host, n in ex.map(worker, jobs):
            print(f"  {host}: {n} ok")
    lf.close()


# ---------------------------------------------------------------- extract
HONORIFIC = re.compile(r"^(?:dr|shri|smt|ms|mrs|mr|sh|kumari|km|prof|col|capt|cdr|lt|gen|brig|maj|sri|shree|thiru|tmt|thirumathi|selvi|janab|mohtarma|er|engr|adv)(?:\.\s*|\s+)", re.I)
SUFFIX = re.compile(r",?\s*\b(?:ias|ips|ifs|irs|ifos|ipos|iras|icas|idas|ies|iss|ites|irts|iss|ioftas|retd\.?)\b\.?", re.I)
DESIG_WORDS = r"(?:secretary|director|officer|commissioner|advis[eo]r|scientist|controller|consultant|member|chairman|" \
              r"chairperson|manager|engineer|registrar|accountant|surveyor|inspector|assistant|deputy|joint|under|" \
              r"additional|principal|executive|head|chief|dean|president|administrator|coordinator|cpio|cvo|" \
              r"economist|statistician|analyst|specialist|superintendent|technical|hydrographer|comptroller|collector)"
DESIG_LINE = re.compile(rf"^\s*\(?\s*(?:{DESIG_WORDS}\b[^\n]{{0,90}})\s*\)?$", re.I)
GOI = re.compile(r"to the gov(?:ernmen)?t\.? of [il]ndia|govt\. of [il]ndia|gov[ea]r?n?ment of [il]ndia", re.I)
NAME_LINE = re.compile(r"^\s*\(?\s*((?:(?:Dr|Shri|Smt|Ms|Mrs|Mr|Sh|Km|Prof)\.?\s+)?[A-Z][A-Za-z.'\-]*(?:\s+[A-Z][A-Za-z.'\-]*){0,4}"
                       r"(?:,?\s*(?:IAS|IPS|IFS|IRS|IPoS|IRAS|IDAS|ICAS|IES|ISS|IFoS))?)\s*\)?\s*$")
STOP_NAME = re.compile(r"\b(?:government|ministry|department|india|delhi|office|section|room|tel|fax|email|e-mail|phone|copy|"
                       r"annexure|page|dated|date|subject|sub|order|notification|circular|memorandum|bhawan|bhavan|new|"
                       r"the|of|to|for|and|all|sd|secretary|director|officer|commissioner|under|joint|deputy|additional|"
                       r"signed|digitally|reason|location|encl|enclosure|yours|faithfully|sincerely|regards|list|no|f|"
                       r"dear|sir|madam|block|floor|wing|marg|road|nagar|puram|pdf|www|gov|nic|in|com|telephone|mobile|division|seal|"
                       r"foundation|gazette|trade|welfare|reliance|limited|ltd|pvt|india|bharat|sarkar|mantralaya|vibhag|guard|file|spare|"
                       r"copies|grid|solar|rooftop|matter|programmes?|special|proper|bedding|write|performance|guarantee|scheme|"
                       r"project|mission|national|state|central|policy|rules|head|fund|bank|authority|board|council|corporation|"
                       r"institute|university|company|centre|center|cell|unit|wing|zone|region|annex|appendix|table|form|format|bid|clause|"
                       r"speakers?|settlement|authori[sz]ed|district|college|hospital|medical|level|details|creator|quote|zero|only|"
                       r"created|deviation|note|key|tender|financial|member|members|copy|forwarded|enclosed|attached|signature|"
                       r"signed|stamp|place|time|venue|total|amount|rupees|lakh|crore|city|incharge|in-charge|production|committee|"
                       r"authorization|authorisation|collectorate|municipal|panchayat|block|tehsil|taluk|mandal)\b", re.I)
SUBJECT = re.compile(r"(?:^|\n)\s*(?:sub(?:ject)?|विषय)\s*[:.\-–—]+\s*(.+?)(?=\n\s*\n|\n\s*(?:sir|madam|ref|reference|the undersigned|i am directed|in continuation|in pursuance|whereas|1\.)\b)", re.I | re.S)
NUMBER = re.compile(r"(?:F\.?\s*No\.?|No\.?|File\s*No\.?)\s*[:.\-]?\s*([A-Z0-9][A-Z0-9/\-().\s]{4,40}?)(?=\s{2,}|\n|dated|Dated|Date)", re.I)


_WORDS = None


def all_dictionary_words(name):
    """True when every token (len>2) is an ordinary lowercase English word in /usr/share/dict/words."""
    global _WORDS
    if _WORDS is None:
        try:
            _WORDS = {w.strip() for w in open("/usr/share/dict/words") if w[:1].islower()}
        except Exception:
            _WORDS = set()
    toks = [t for t in re.findall(r"[A-Za-z]+", name) if len(t) > 2]
    return bool(toks) and bool(_WORDS) and all(t.lower() in _WORDS for t in toks)


def clean_name(s):
    s = unicodedata.normalize("NFKC", s).replace("(", "").replace(")", "").strip(" .,-")
    s = SUFFIX.sub("", s)
    s = HONORIFIC.sub("", s)
    s = HONORIFIC.sub("", s)
    s = re.sub(r"[\s,.]+\b(?:jt|it|dy|addl|under|joint|deputy|secy|us|ds|js)\b\.?$", "", s, flags=re.I)
    return re.sub(r"\s+", " ", s).strip(" .,-")


def pdf_text(path, pages_tail=2):
    path = Path(path)
    cache = path.parent.parent / "text" / (path.stem + ".json")
    if cache.exists():
        try:
            c = json.loads(cache.read_text())
            pdf_text.last_ocr = c.get("ocr", False)
            return c["n"], c["head"], c["tail"]
        except Exception:
            pass
    n, head, tail = _pdf_text(path, pages_tail)
    try:
        cache.parent.mkdir(exist_ok=True)
        cache.write_text(json.dumps({"n": n, "head": head, "tail": tail, "ocr": pdf_text.last_ocr}, ensure_ascii=False))
    except Exception:
        pass
    return n, head, tail


def _pdf_text(path, pages_tail=2):
    try:
        info = subprocess.run(["pdfinfo", str(path)], capture_output=True, text=True, timeout=60).stdout
        n = int(re.search(r"Pages:\s+(\d+)", info).group(1)) if "Pages:" in info else 1
    except Exception:
        n = 1
    def run(args):
        try:
            return subprocess.run(["pdftotext", "-layout", *args, str(path), "-"], capture_output=True, text=True, timeout=120).stdout
        except Exception:
            return ""
    head = run(["-f", "1", "-l", str(min(2, n))])
    tail = run(["-f", str(max(1, n - pages_tail + 1)), "-l", str(n)]) if n > 2 else head
    ocr = False
    if len(re.sub(r"\s", "", head + tail)) < 80 and n <= 60:
        ocr = True
        head = ocr_pages(path, 1, 1) or head
        tail = (ocr_pages(path, n, n) if n > 1 else head) or tail
    pdf_text.last_ocr = ocr
    head = head.replace("\u200c", "").replace("\u200d", "")
    tail = tail.replace("\u200c", "").replace("\u200d", "")
    return n, head, tail


def ocr_pages(path, first, last):
    """tesseract (eng) over rendered pages; returns '' when tools are missing."""
    import tempfile
    try:
        with tempfile.TemporaryDirectory() as td:
            subprocess.run(["pdftoppm", "-r", "200", "-gray", "-f", str(first), "-l", str(last), str(path), f"{td}/p"],
                           capture_output=True, timeout=120)
            out = []
            for img in sorted(Path(td).glob("p*.p*m")):
                r = subprocess.run(["tesseract", str(img), "-", "-l", OCR_LANG, "--psm", "6"], capture_output=True, text=True, timeout=180)
                out.append(r.stdout)
            return "\n".join(out)
    except Exception:
        return ""


DESIG_ABBR = r"(?:jt|it|joint|dy|deputy|under|addl|additional|principal|spl|special|sr|senior|asstt|assistant|executive)?\.?\s*(?:secy|secretary|director|commissioner|us|ds|js|das|osd|registrar|controller|advis[eo]r|scientist|engineer|officer|manager|dg|ddg|adg|director general)\b"
# a designation that is the WHOLE remainder of the line: "Jt. Secy.", "Under Secretary (Cadre)", "Director (A&D)",
# "Deputy Secretary to the Govt. of India", "Under Secy. [F. No. ...]"
DESIG_STRICT = re.compile(rf"^(?i:{DESIG_ABBR}(?:\s*(?:\([^)]{{1,40}}\)|-[A-Z]{{1,6}}|\s*&\s*[A-Za-z. ]{{1,30}}))?\.?(?:\s*(?:to|,)?\s*(?:the\s+)?gov(?:ernmen)?t\.?\s*of\s+india\.?)?(?:\s*\[[^\]]{{0,60}}\]?)?\s*)$")
INLINE_SIG = re.compile(r"^\s*\(?((?:(?:Dr|Shri|Smt|Ms|Mrs|Mr|Sh|Km|Prof)\.?\s+)?[A-Z][A-Za-z'\-]*\.?(?:\s+[A-Z][A-Za-z'\-]*\.?){1,4})\)?[,.\s]+([A-Za-z][^\n]{1,70})$")
VERBISH = re.compile(r"\b(?:is|are|shall|may|will|has|have|was|were|be|posted|transferred|promoted|appointed|vice|column|ensure|compliance)\b", re.I)

DIGSIG = re.compile(r"digitally signed by[:\s]+([A-Z][A-Za-z.'\- ]{3,50}?)(?=\s{2,}|\n|Date|date|$)", re.M)


def _name_from_line(line):
    """Pull the Latin name out of a (possibly bilingual / OCR-noisy) signature line."""
    s = line.strip()
    if len(s) > 80:
        return None, False
    has_paren = s.endswith(")")
    s = s.strip("()* ")
    if "/" in s:                      # हिंदी नाम/English Name
        s = s.split("/")[-1]
    s = re.sub(r"^[^A-Za-z]+", "", s).strip(" .,:-")
    m = re.fullmatch(r"(?:(?:Dr|Shri|Smt|Ms|Mrs|Mr|Sh|Km|Prof)\.?\s+)?([A-Z][A-Za-z.'\-]*(?:\s+[A-Z][A-Za-z.'\-]*){1,4})"
                     r"(?:,?\s*(?:IAS|IPS|IFS|IRS|IPoS|IRAS|IDAS|ICAS|IES|ISS|IFoS))?", s)
    if not m:
        return None, has_paren
    name = clean_name(m.group(1))
    if len(name) < 5 or STOP_NAME.search(name) or all_dictionary_words(name):
        return None, has_paren
    return name, has_paren


def find_signatories(tail):
    """Return list of (name, designation, strength, line_no) found in signature-block position."""
    lines = [l.rstrip() for l in tail.splitlines()]
    found = []
    for i, line in enumerate(lines):
        if not line.strip():
            continue
        # one-line gazette style: "RAJBIR SINGH RANA, Jt. Secy."  /  "A. K. Singh, Director"
        im = INLINE_SIG.match(line.strip())
        if im and DESIG_STRICT.match(im.group(2).strip()):
            name = clean_name(im.group(1))
            if len(name) >= 5 and not STOP_NAME.search(name) and len(name.split()) >= 2 and not all_dictionary_words(name):
                found.append((name, re.sub(r"\s+", " ", im.group(2)).strip(" .,"), 4, i))
                continue
        name, has_paren = _name_from_line(line)
        if not name or len(name.split()) < 2:
            continue
        nxt = [l.strip() for l in lines[i + 1:i + 5] if l.strip()][:3]
        desig = None
        for cand in nxt:
            c = cand.split("/")[-1].strip("() ") if "/" in cand else cand.strip("() ")
            c = re.sub(r"^[^A-Za-z]+", "", c)
            if VERBISH.search(c) or re.search(r"\d{5,}", c):
                continue
            c = c.replace("lndia", "India").replace("Govemment", "Government")
            dm = re.search(rf"(?i:{DESIG_ABBR})", c)      # tolerate OCR / Hindi garbage before the designation
            c2 = c[dm.start():].strip() if dm else c
            if DESIG_STRICT.match(c2) or (DESIG_LINE.match(c2) and len(c2) <= 60):
                desig = re.sub(r"\s+", " ", c2); break
            if GOI.search(c) and len(c) < 90:
                desig = c; break
        prev = lines[i - 1].strip().lower() if i else ""
        sd = "sd/" in prev or prev.startswith("sd.") or prev.endswith("sd")
        goi_only = bool(desig) and not (DESIG_STRICT.match(desig) or DESIG_LINE.match(desig))
        strength = (1 if goi_only else 3 if desig else 0) + (2 if has_paren else 0) + (1 if sd else 0) + (1 if desig and GOI.search(desig) else 0)
        if strength >= 3:
            found.append((name, desig or "", strength, i))
    return found


def digital_signer(text):
    m = DIGSIG.findall(text)
    return clean_name(m[-1]) if m else ""


def extract():
    cand = pd.read_csv(OUT / "candidates.csv").set_index("doc_id")
    out_path = OUT / "signatures.csv"
    done = set(pd.read_csv(out_path).doc_id) if out_path.exists() else set()
    rows = []
    files = sorted(PDF.glob("*.pdf"))
    print(f"extract: {len(files)} PDFs, {len(done)} already done")
    for k, f in enumerate(files):
        did = f.stem
        if did in done or did not in cand.index:
            continue
        n, head, tail = pdf_text(f)
        ocr_used = pdf_text.last_ocr
        text_chars = len(re.sub(r"\s", "", head))
        deva = len(re.findall(r"[ऀ-ॿ]", head))
        subj = SUBJECT.search(head)
        subj = re.sub(r"\s+", " ", subj.group(1)).strip()[:300] if subj else ""
        num = NUMBER.search(head)
        num = re.sub(r"\s+", " ", num.group(1)).strip() if num else ""
        sigs = find_signatories(tail)
        dsig = digital_signer(tail) or digital_signer(head)
        base = dict(doc_id=did, pages=n, text_chars=text_chars, devanagari_chars=deva, scanned=int(text_chars < 80 and not ocr_used), ocr=int(ocr_used),
                    file_number=num, subject=subj, digital_signer=dsig)
        contact = {}
        if sigs:
            tl = tail.splitlines()
            for nm, dg, stv, i in sigs:
                blk = " ".join(tl[i:i + 7])
                em = re.search(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+|[\w.+-]+\[at\][\w-]+(?:\[dot\][\w-]+)+", blk, re.I)
                ph = re.search(r"(?:tel|phone|ph|mob|mobile|telefax|fax)[\s.:-]*([+\d][\d\s\-/,()]{6,30}\d)", blk, re.I)
                contact[nm] = (em.group(0).replace("[at]", "@").replace("[dot]", ".") if em else "", re.sub(r"\s+", " ", ph.group(1)).strip() if ph else "")
        if not sigs and dsig and len(dsig.split()) >= 2 and not STOP_NAME.search(dsig):
            # e-office documents often carry only the DSC stamp; use it, marked as such
            rows.append({**base, "sig_rank": 1, "signatory": dsig, "sig_designation": "(digital signature only)", "strength": 2})
        elif not sigs:
            rows.append({**base, "sig_rank": 0, "signatory": "", "sig_designation": "", "strength": 0})
        else:
            # the LAST strong block on the final pages is the signatory; keep up to 3 (counter-signs / multiple)
            sigs = sorted(sigs, key=lambda x: (-x[3]))[:3]
            for r, (nm, dg, st, _) in enumerate(sigs, 1):
                em, ph = contact.get(nm, ("", ""))
                rows.append({**base, "sig_rank": r, "signatory": nm, "sig_designation": dg, "strength": st, "sig_email": em, "sig_phone": ph})
        if (k + 1) % 100 == 0:
            print(f"  {k+1}/{len(files)}")
    df = pd.DataFrame(rows)
    if out_path.exists() and done:
        df = pd.concat([pd.read_csv(out_path), df], ignore_index=True)
    df.to_csv(out_path, index=False)
    got = df[df.sig_rank == 1]
    print(f"extract: {df.doc_id.nunique()} docs, {len(got)} with a signatory, "
          f"{int(df.drop_duplicates('doc_id').scanned.sum())} scanned/no-text")


# ---------------------------------------------------------------- directory (names from the documents themselves)
def directory():
    """Aggregate every signatory read from the PDFs into a who-signs-what directory, independent of any roster."""
    sig = pd.read_csv(OUT / "signatures.csv")
    cand = pd.read_csv(OUT / "candidates.csv").set_index("doc_id")
    sig = sig[sig.sig_rank > 0].join(cand[["ministry", "title", "date", "url"]], on="doc_id")
    sig["name_key"] = sig.signatory.astype(str).map(lambda x: " ".join(norm_tokens(x)))
    sig = sig[sig.name_key.str.len() >= 5]
    ns_path = OUT / "notification_signatories.csv"
    matched = {}
    if ns_path.exists():
        ns = pd.read_csv(ns_path)
        ns = ns[ns.match_status == "matched"]
        for r in ns.itertuples():
            matched.setdefault((r.doc_id, r.signatory), (r.officer_name, r.officer_designation, r.officer_email, r.confidence))
    rows = []
    for (mn, key), g in sig.groupby(["ministry", "name_key"]):
        g = g.sort_values("date", ascending=False, na_position="last")
        desigs = [d for d in g.sig_designation.dropna().astype(str) if d and not d.startswith("(digital")]
        mm = [matched[k] for k in zip(g.doc_id, g.signatory) if k in matched]
        rows.append(dict(ministry=mn, signatory=g.signatory.mode().iat[0], name_variants=" | ".join(sorted(set(g.signatory.astype(str)))[:5]),
                         designations=" | ".join(pd.Series(desigs).value_counts().index[:3]) if desigs else "",
                         n_documents=g.doc_id.nunique(), first_date=g.date.dropna().min(), last_date=g.date.dropna().max(),
                         email=next((e for e in g.get("sig_email", pd.Series(dtype=str)).dropna().astype(str) if e), ""),
                         phone=next((p for p in g.get("sig_phone", pd.Series(dtype=str)).dropna().astype(str) if p), ""),
                         roster_match=mm[0][0] if mm else "", roster_designation=mm[0][1] if mm else "", roster_email=mm[0][2] if mm else "",
                         match_confidence=mm[0][3] if mm else "", topics="; ".join(sorted({t for s_ in (g.subject.fillna("") + " | " + g.title.fillna("")) for t in topic_of(s_)})[:4]),
                         example_titles=" || ".join(g.title.fillna("").astype(str).str[:100].head(3)), document_urls=" ".join(g.url.head(5))))
    df = pd.DataFrame(rows).sort_values(["ministry", "n_documents"], ascending=[True, False])
    df.to_csv(OUT / "signatory_directory.csv", index=False)
    print(f"directory: {len(df)} distinct signers across {df.ministry.nunique()} ministries; {int((df.roster_match != '').sum())} already matched to a roster; "
          f"{int((df.email != '').sum())} with an email printed under the signature")


# ---------------------------------------------------------------- match
def norm_tokens(name):
    n = clean_name(name).lower()
    n = unicodedata.normalize("NFKD", n).encode("ascii", "ignore").decode()
    n = re.sub(r"[^a-z ]", " ", n.replace(".", " "))
    # phonetic folding of common Indian-English spelling variants (Apoorva/Apurva, Sreedhar/Sridhar, Varma/Verma)
    n = n.replace("oo", "u").replace("ee", "i").replace("aa", "a").replace("w", "v").replace("ck", "k").replace("ph", "f")
    n = re.sub(r"\bsh", "s", n).replace("th", "t").replace("dh", "d").replace("bh", "b").replace("gh", "g").replace("kh", "k")
    n = re.sub(r"(?<=[^aeiou])e(?=r?\b)", "a", n)
    return [t for t in n.split() if t]


def name_sim(a, b):
    """Token-level similarity: every token of the shorter name must be accounted for
    (exact = 1, OCR-fuzzy = 0.9, initial = 0.8); divided by the longer token count."""
    ta, tb = norm_tokens(a), norm_tokens(b)
    if not ta or not tb:
        return 0.0
    if ta == tb:
        return 1.0
    short, long_ = (ta, tb) if len(ta) <= len(tb) else (tb, ta)
    used = set(); got = 0.0
    for t in short:
        best, bj = 0.0, None
        for j, u in enumerate(long_):
            if j in used:
                continue
            if t == u:
                sc = 1.0
            elif len(t) == 1 and u.startswith(t):
                sc = 0.8
            elif len(u) == 1 and t.startswith(u):
                sc = 0.8
            elif len(t) > 3 and len(u) > 3 and SequenceMatcher(None, t, u).ratio() >= 0.85:
                sc = 0.9
            else:
                sc = 0.0
            if sc > best:
                best, bj = sc, j
        if bj is not None:
            used.add(bj); got += best
    score = got / len(long_)
    ja, jb = "".join(ta), "".join(tb)          # OCR dropped/merged spaces
    if min(len(ja), len(jb)) > 10:
        jr = SequenceMatcher(None, ja, jb).ratio()
        if jr >= 0.9:
            score = max(score, jr)
    return round(score, 3)


RANK = [("secretary", 6), ("additional secretary", 5), ("special secretary", 5), ("joint secretary", 4),
        ("director", 3), ("deputy secretary", 2), ("under secretary", 1), ("section officer", 0)]


def rank_of(desig):
    d = re.sub(r"[^a-z ]", " ", str(desig).lower()); d = " " + re.sub(r"\s+", " ", d).strip() + " "
    d = d.replace(" jt ", " joint ").replace(" dy ", " deputy ").replace(" addl ", " additional ").replace("secy", "secretary")
    if re.search(r"\b(?:ps|pps|aps|pa) to\b|private secretary|personal secretary|secretary to (?:the )?(?:minister|chairman|hon)", d):
        return None
    for key, r in sorted(RANK, key=lambda x: -len(x[0])):
        if " " + key + " " in d:
            if key == "secretary" and re.search(r"(?:under|deputy|joint|additional|special) secretary", d):
                continue
            return r
    return None


CENTRAL = re.compile(r"\b(?:goi|govt\.? of india|government of india|new delhi|central deputation|ministry of|m/o|d/o|department of)\b", re.I)


def load_rosters():
    R = []
    m = pd.read_csv(REPO / "data/ministry_officials.csv")
    for r in m.itertuples():
        R.append(dict(roster="ministry_whoswho", ministry=r.ministry, name=r.name, designation=r.designation,
                      division=r.division if isinstance(r.division, str) else "", email=r.email if isinstance(r.email, str) else "",
                      phones=r.phones if isinstance(r.phones, str) else "", source_url=r.source_url))
    o = pd.read_csv(REPO / "data/officials.csv")
    for r in o.itertuples():
        R.append(dict(roster="igod_officials", ministry=r.org_name, name=r.name, designation=r.designation,
                      division=r.division if isinstance(r.division, str) else "", email=r.email if isinstance(r.email, str) else "",
                      phones=r.phones if isinstance(r.phones, str) else "", source_url=f"https://igod.gov.in/organization/{r.igod_org_id}"))
    for fn, tag in (("ias_officers.csv", "ias_civil_list"), ("ips_officers.csv", "ips_civil_list")):
        p = REPO / "data" / fn
        if not p.exists():
            continue
        c = pd.read_csv(p, low_memory=False)
        for r in c.itertuples():
            R.append(dict(roster=tag, ministry=str(getattr(r, "current_posting", "") or ""), name=r.name_en,
                          designation=str(getattr(r, "current_posting", "") or ""), division="", email="", phones="",
                          source_url=str(getattr(r, "er_sheet_url", "") or "")))
    df = pd.DataFrame(R)
    df = df[df.name.notna() & (df.name.astype(str).str.strip() != "")]
    df["name_clean"] = df.name.astype(str).map(clean_name)
    df = df[~df.name_clean.str.fullmatch(r"-+|\.*|nil|vacant", case=False)]
    df["officer_id"] = df.apply(lambda r: hashlib.sha1(f"{r.roster}|{r.ministry}|{r.name_clean}|{r.designation}".encode()).hexdigest()[:10], axis=1)
    return df.reset_index(drop=True)


def ministry_key(s):
    s = str(s).lower()
    s = re.sub(r"\(.*?\)", "", s)
    s = re.sub(r"\b(?:ministry|department|dept|of|the|and|&|for)\b", " ", s)
    return set(t for t in re.split(r"[^a-z]+", s) if len(t) > 3)


def match():
    sig = pd.read_csv(OUT / "signatures.csv")
    cand = pd.read_csv(OUT / "candidates.csv").set_index("doc_id")
    ros = load_rosters()
    ros.to_csv(OUT / "roster_union.csv", index=False)
    print(f"match: roster union {len(ros)} officers; {sig[sig.sig_rank>0].shape[0]} signatures")
    by_first = defaultdict(list)
    for i, r in ros.iterrows():
        toks = norm_tokens(r.name_clean)
        for t in set(toks):
            if len(t) > 1:
                by_first[t].append(i)
    rows = []
    for s in sig[sig.sig_rank > 0].itertuples():
        toks = norm_tokens(s.signatory)
        doc_min = cand.loc[s.doc_id, "ministry"] if s.doc_id in cand.index else ""
        mk = ministry_key(doc_min)
        pool = set()
        for t in toks:
            if len(t) > 1:
                pool.update(by_first.get(t, []))
        best = []
        for i in pool:
            r = ros.loc[i]
            sc = name_sim(s.signatory, r.name_clean)
            if sc < 0.6:
                continue
            same_min = bool(mk & ministry_key(r.ministry)) or (r.roster == "ministry_whoswho" and r.ministry == doc_min)
            if r.roster in ("ias_civil_list", "ips_civil_list") and not CENTRAL.search(str(r.ministry)):
                continue                              # posted in a state: cannot be signing a union-ministry OM
            rs, rr = rank_of(s.sig_designation), rank_of(r.designation)
            if rs is not None and rr is not None and abs(rs - rr) >= 2:
                continue                              # Under Secretary vs Secretary etc.: different person
            rank_pen = 0.15 if (rs is not None and rs >= 4 and rr is None) else 0
            desig_ok = 0
            if isinstance(s.sig_designation, str) and s.sig_designation and isinstance(r.designation, str):
                a = set(norm_tokens(s.sig_designation)) - {"to", "the", "of", "government", "india", "govt"}
                b = set(norm_tokens(r.designation))
                desig_ok = 1 if (a & b) and (rs is None or rr is None or rs == rr) else 0
            total = sc - rank_pen + (0.25 if same_min else 0) + (0.1 if desig_ok else 0) + (0.05 if r.roster == "ministry_whoswho" else 0)
            best.append((total, sc, same_min, desig_ok, i))
        best.sort(reverse=True)
        if not best:
            rows.append(dict(doc_id=s.doc_id, sig_rank=s.sig_rank, signatory=s.signatory, sig_designation=s.sig_designation,
                             match_status="unmatched", officer_id="", officer_name="", officer_designation="", officer_ministry="",
                             officer_division="", officer_email="", officer_phones="", roster="", name_score=0, same_ministry=0, desig_match=0, confidence=""))
            continue
        total, sc, same_min, desig_ok, i = best[0]
        r = ros.loc[i]
        ntok = len(norm_tokens(s.signatory))
        if sc >= 0.95 and same_min and not rank_pen:
            conf = "high"
        elif sc >= 0.8 and same_min:
            conf = "medium"
        elif sc >= 0.98 and ntok >= 3 and not rank_pen:
            conf = "low (name only, other ministry)"
        else:
            conf = "weak"
        if conf == "weak":
            status = "unmatched"
        else:
            status = "matched"
        rows.append(dict(doc_id=s.doc_id, sig_rank=s.sig_rank, signatory=s.signatory, sig_designation=s.sig_designation,
                         match_status=status, officer_id=r.officer_id if status == "matched" else "",
                         officer_name=r["name"] if status == "matched" else "", officer_designation=r.designation if status == "matched" else "",
                         officer_ministry=r.ministry if status == "matched" else "", officer_division=r.division if status == "matched" else "",
                         officer_email=r.email if status == "matched" else "", officer_phones=r.phones if status == "matched" else "",
                         roster=r.roster if status == "matched" else "", name_score=round(sc, 2), same_ministry=int(same_min),
                         desig_match=desig_ok, confidence=conf if status == "matched" else f"rejected ({conf}, best={r['name']})"))
    out = pd.DataFrame(rows)
    meta = cand[["ministry", "title", "group", "category", "date", "url"]]
    out = out.join(meta, on="doc_id")
    sub = sig[["doc_id", "sig_rank", "subject", "file_number", "scanned"]]
    out = out.merge(sub, on=["doc_id", "sig_rank"], how="left")
    out.to_csv(OUT / "notification_signatories.csv", index=False)
    print(out.match_status.value_counts().to_string()); print(out[out.match_status == "matched"].confidence.value_counts().to_string())


# ---------------------------------------------------------------- matrix
TOPICS = [
    ("HR: appointment / transfer / posting / promotion", r"appoint|transfer|posting|promot|deputation|joining|relieve|reliev|empanel|seniority|vacanc|recruit|probation|retire|superannuat|extension of (?:service|tenure)|charge of the post"),
    ("HR: leave / pay / allowances / service rules", r"leave|pay|allowance|increment|pension|gpf|ltc|hra|da\b|dearness|medical reimburse|service rules|conduct rules|acr|apar"),
    ("Recruitment rules / RRs", r"recruitment rules|\brrs?\b"),
    ("RTI / appellate authority / CPIO", r"\brti\b|cpio|appellate|first appeal|information officer|transparency officer"),
    ("Procurement / tenders / GeM", r"tender|procure|\bgem\b|bid|rfp|eoi|expression of interest|quotation|empanelment of (?:agenc|vendor)"),
    ("Budget / sanction / release of funds / grants", r"sanction|release of (?:fund|grant|amount)|grant-in-aid|grants-in-aid|budget|expenditure|utili[sz]ation certificate|\buc\b|re-appropriation|funds"),
    ("Statutory rules / gazette notifications (G.S.R. / S.O.)", r"g\.s\.r|s\.o\.|gazette|rules, ?\d{4}|\(amendment\) rules|notified|hereby notif|in exercise of the powers|commencement"),
    ("Acts / commencement / legislation", r"\bact\b|ordinance|bill|commencement notification|section \d+"),
    ("Customs / tariff / duty / GST", r"customs|tariff|duty|\bgst\b|cess|excise|exemption from"),
    ("Scheme guidelines / implementation", r"scheme|guideline|sop|standard operating|implementation|operational guidelines|component|subsidy|incentive|\bpli\b"),
    ("Committees / meetings / minutes / constitution of", r"committee|constitut|meeting|minutes|task force|working group|nodal officer|reconstitut"),
    ("Advisory / public notice / caution", r"advisory|public notice|caution|alert|fraud|fake|clarification"),
    ("Licensing / approvals / standards / enlistment", r"licen[cs]e|approval|approved list|almm|enlist|registration|certif|standard|bis\b|quality control order|\bqco\b"),
    ("Legal metrology / consumer protection rules", r"legal metrology|packaged commodities|consumer protection|weights and measures"),
    ("Office administration / housekeeping", r"office order|holiday|working hours|attendance|biometric|canteen|parking|security|identity card|dak|e-office|library|telephone|vehicle"),
    ("Training / capacity building / workshops", r"training|workshop|capacity building|seminar|webinar|conference|nomination"),
    ("Vigilance / disciplinary / court matters", r"vigilance|disciplinar|charge sheet|court|contempt|writ|\bcat\b|tribunal|litigation|legal (?!metrology)"),
    ("Parliament / VIP references / reports", r"parliament|lok sabha|rajya sabha|assurance|vip reference|annual report|monthly report|progress report"),
]


def topic_of(text):
    t = str(text).lower()
    hits = [name for name, pat in TOPICS if re.search(pat, t)]
    return hits[:2] if hits else ["Other / unclassified"]


def matrix():
    ns = pd.read_csv(OUT / "notification_signatories.csv")
    m = ns[ns.match_status == "matched"].copy()
    m["topic_text"] = m.subject.fillna("") + " | " + m.title.fillna("") + " | " + m.group.fillna("") + " | " + m.category.fillna("")
    m["topics"] = m.topic_text.map(topic_of)
    ex = m.explode("topics")
    rows = []
    for (oid, topic), g in ex.groupby(["officer_id", "topics"]):
        r = g.iloc[0]
        g2 = g.sort_values("date", ascending=False)
        rows.append(dict(officer_id=oid, officer_name=r.officer_name, officer_designation=r.officer_designation,
                         officer_ministry=r.officer_ministry, officer_division=r.officer_division, officer_email=r.officer_email,
                         officer_phones=r.officer_phones, roster=r.roster, topic=topic, n_documents=g.doc_id.nunique(),
                         first_date=g.date.dropna().min(), last_date=g.date.dropna().max(),
                         signed_as=" / ".join(sorted(set(x for x in g.sig_designation.dropna().astype(str) if x))[:3]),
                         confidence=" / ".join(sorted(set(g.confidence))),
                         example_titles=" || ".join(g2.title.fillna("").astype(str).str[:120].head(3)),
                         document_urls=" ".join(g2.url.head(10)),
                         doc_ids=" ".join(g2.doc_id.head(50))))
    mx = pd.DataFrame(rows).sort_values(["officer_ministry", "officer_name", "n_documents"], ascending=[True, True, False])
    mx.to_csv(OUT / "officer_topic_matrix.csv", index=False)
    piv = ex.pivot_table(index=["officer_ministry", "officer_name", "officer_designation", "officer_email"], columns="topics",
                         values="doc_id", aggfunc=pd.Series.nunique, fill_value=0)
    piv["TOTAL"] = piv.sum(axis=1)
    piv = piv.sort_values("TOTAL", ascending=False)
    piv.to_csv(OUT / "officer_topic_pivot.csv")
    # per-document long table for the matrix consumers
    m.drop(columns=["topic_text"]).assign(topics=m.topics.map("; ".join)).to_csv(OUT / "officer_documents.csv", index=False)
    write_report(ns, m, ex, mx, piv)
    print(f"matrix: {mx.officer_id.nunique()} officers x {ex.topics.nunique()} topics, {m.doc_id.nunique()} documents")


def write_report(ns, m, ex, mx, piv):
    cand = pd.read_csv(OUT / "candidates.csv")
    sig = pd.read_csv(OUT / "signatures.csv")
    fetched = len(list(PDF.glob("*.pdf")))
    with_sig = sig[sig.sig_rank == 1].doc_id.nunique()
    lines = []
    L = lines.append
    L("# Who signed what — officers ↔ orders / notifications matrix\n")
    L(f"_Built {time.strftime('%Y-%m-%d')} by `scripts/signatory_matrix.py`. Scope: ministries with a who's-who roster in "
      f"`data/ministry_officials.csv` ({cand.ministry.nunique()} ministries/departments)._\n")
    L("## Funnel\n")
    L("| Stage | Count |\n|---|---|")
    L(f"| Candidate order/notification/circular/OM/gazette PDFs in the document index | {len(cand)} |")
    L(f"| PDFs fetched | {fetched} |")
    L(f"| PDFs with machine-readable text | {int((sig.drop_duplicates('doc_id').scanned == 0).sum())} |")
    L(f"| PDFs with a detectable signature block | {with_sig} |")
    L(f"| Signatures matched to a roster officer | {ns[ns.match_status=='matched'].doc_id.nunique()} documents / {m.officer_id.nunique()} officers |")
    L(f"| Signatures not matched (person not in any roster, or moved) | {ns[ns.match_status=='unmatched'].doc_id.nunique()} |")
    L("")
    L("## Per ministry\n")
    L("| Ministry | candidates | fetched | signature found | matched docs | officers linked |\n|---|---|---|---|---|---|")
    sig1 = sig[sig.sig_rank == 1][["doc_id"]].merge(cand[["doc_id", "ministry"]], on="doc_id")
    for mn, g in cand.groupby("ministry"):
        f = sum((PDF / f"{d}.pdf").exists() for d in g.doc_id)
        s = sig1[sig1.ministry == mn].doc_id.nunique()
        mm = ns[(ns.match_status == "matched") & (ns.ministry == mn)]
        L(f"| {mn} | {len(g)} | {f} | {s} | {mm.doc_id.nunique()} | {mm.officer_id.nunique()} |")
    L("")
    L("## Officer × topic matrix (documents signed)\n")
    L("Full pivot: `officer_topic_pivot.csv`; long form with example titles and URLs: `officer_topic_matrix.csv`; "
      "one row per signed document: `officer_documents.csv`.\n")
    top = piv.head(40)
    cols = [c for c in top.columns if c != "TOTAL"]
    keep = [c for c in cols if top[c].sum() > 0]
    L("| Officer | Designation (roster) | Ministry | " + " | ".join(keep) + " | TOTAL |")
    L("|---|---|---|" + "---|" * (len(keep) + 1))
    for idx, r in top.iterrows():
        mn, nm, dg, em = idx
        L(f"| {nm} | {dg} | {mn} | " + " | ".join(str(int(r[c])) if r[c] else "" for c in keep) + f" | {int(r['TOTAL'])} |")
    L("")
    L("## Contact person by topic\n")
    L("For each ministry and topic, the roster officers who signed the most documents on it (name, roster designation, email).\n")
    for mn, g in ex.groupby("officer_ministry"):
        L(f"### {mn}\n")
        L("| Topic | Contact officers (docs signed) |\n|---|---|")
        for tp, gg in g.groupby("topics"):
            c = gg.groupby(["officer_name", "officer_designation", "officer_email"]).doc_id.nunique().sort_values(ascending=False).head(4)
            cell = "; ".join(f"**{n}** — {d}{(' — ' + e) if isinstance(e, str) and e else ''} ({k})" for (n, d, e), k in c.items())
            L(f"| {tp} | {cell} |")
        L("")
    L("## Signatories missing from the rosters (roster gaps)\n")
    L("People who sign orders for a ministry but are not on its who's-who page / igod / civil lists — candidates to add to the yellow pages.\n")
    L("| Ministry | Signatory (as printed) | Signed as | Documents | Latest |\n|---|---|---|---|---|")
    u = ns[ns.match_status == "unmatched"].copy()
    u["sig_key"] = u.signatory.map(lambda x: " ".join(norm_tokens(x)))
    for (mn, key), g in sorted(u.groupby(["ministry", "sig_key"]), key=lambda kv: (-kv[1].doc_id.nunique(), kv[0])):
        if g.doc_id.nunique() < 2 or not re.search(r"secretary|secy|director|commissioner|scientist|officer|registrar|advis", " ".join(g.sig_designation.astype(str)), re.I):
            continue
        L(f"| {mn} | {g.signatory.mode().iat[0]} | {' / '.join(sorted(set(g.sig_designation.dropna().astype(str)))[:2])} | {g.doc_id.nunique()} | {g.date.dropna().max() if g.date.notna().any() else ''} |")
    L("")
    L("## Caveats\n")
    L("- A signature block is read heuristically from the last two pages of each PDF: a name line (often in parentheses) "
      "followed by a designation line. Scanned PDFs and Hindi-only signature blocks are not read (counted above).")
    L("- Matching is by name similarity with a bonus for the same ministry and a matching designation; `confidence` is "
      "`high` (near-exact name, same ministry), `medium`, or `low (name only, other ministry)`. Rosters are a snapshot "
      "(who's-who pages, igod, DoPT civil lists), so an officer who signed in 2022 may have moved since.")
    L("- 'Contact person for a topic' means *signed documents on that topic*, not a published point of contact. "
      "Topics are keyword buckets over subject line + title + site category; a document can fall in two buckets.")
    L("- Rows with `match_status=unmatched` in `notification_signatories.csv` are real signatories who are not in any roster — "
      "a useful list of people to add to the yellow pages.")
    (OUT / "SIGNATORY_MATRIX.md").write_text("\n".join(lines))


if __name__ == "__main__":
    stages = sys.argv[1:] or ["all"]
    if stages == ["all"]:
        stages = ["select", "fetch", "extract", "directory", "match", "matrix", "directory"]
    for s in stages:
        globals()[s]()
