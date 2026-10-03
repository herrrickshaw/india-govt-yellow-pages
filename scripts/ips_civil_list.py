#!/usr/bin/env python3
"""IPS Civil List (MHA) — one officer per row, all 25 cadres.

ips.gov.in has no searchable web UI (despite what third-party aggregators
imply) — the real source is a single static PDF (Empanelment/CivilList<year>.pdf)
that needs a session cookie from the homepage first, or the direct fetch
302s to an error page.

The PDF has a real text layer laid out in a repeating 6-column table
((1) Sr.No (2) Name/Qualification (3) Source/Code/Domicile
 (4) DOB/AppointmentDate/PayScale (5) Posting (6) Awards), with the
"(1)..(6)" header re-printed on every page — so column x-positions are
recovered per page from that header rather than assumed fixed.

Output: data/ips_officers.csv
"""
import csv
import re
import sys
import time
from pathlib import Path

import pdfplumber
import requests

DATA = Path(__file__).resolve().parent.parent / "data"
PDF_PATH = DATA / "CivilList_IPS.pdf"
OUT = DATA / "ips_officers.csv"
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0 Safari/537.36")
HOME_URL = "https://ips.gov.in/"
LIST_PAGE_URL = "https://ips.gov.in/ips_civillist.aspx"
PDF_URL_RE = re.compile(r'href="([^"]*CivilList[^"]*\.pdf)"', re.I)

SOURCE_CODES = {"RR", "SPS", "SDPS", "LDCE", "DR", "PROM", "AD-HOC", "AD"}

# the 25 real IPS cadres (from the civil list's own table of contents) — the
# Authorised-Cadre-Strength appendix tables also carry a "(1)..(6)"-shaped
# header by coincidence and must be filtered out, not treated as officer data
VALID_CADRES = {
    "Andhra Pradesh", "Arunachal Pradesh-Goa-Mizoram-UTs", "Assam-Meghalaya",
    "Bihar", "Chhattisgarh", "Gujarat", "Haryana", "Himachal Pradesh",
    "Jharkhand", "Karnataka", "Kerala", "Madhya Pradesh", "Maharashtra",
    "Manipur", "Nagaland", "Odisha", "Punjab", "Rajasthan", "Sikkim",
    "Tamil Nadu", "Telangana", "Tripura", "Uttar Pradesh", "Uttarakhand",
    "West Bengal",
}
DATE_RE = re.compile(r"^\d{2}/\d{2}/\d{4}$")
YEAR_HEADER_RE = re.compile(r"Allotment\s+Year\s*:\s*(\d{4})", re.I)
CODE_RE = re.compile(r"^\d{6,9}$")

FIELDS = [
    "cadre_state", "allotment_year", "sr_no", "name_en", "name_hi",
    "source_of_recruitment", "officer_code", "appointment_date", "dob",
    "qualification", "domicile_state", "pay_scale", "current_posting",
    "posting_wef", "awards",
]

ROW_BAND_TOL = 3.0  # points; words within this of each other's `top` share a row band


def resolve_pdf_url(session):
    r = session.get(HOME_URL, timeout=60)
    r.raise_for_status()
    r = session.get(LIST_PAGE_URL, timeout=60, headers={"Referer": HOME_URL})
    r.raise_for_status()
    m = PDF_URL_RE.search(r.text)
    if not m:
        raise RuntimeError("could not find CivilList PDF link on ips_civillist.aspx")
    return LIST_PAGE_URL.rsplit("/", 1)[0] + "/" + m.group(1)


def download_pdf(force=False):
    if PDF_PATH.exists() and not force:
        return PDF_PATH
    session = requests.Session()
    session.headers.update({"User-Agent": UA})
    pdf_url = resolve_pdf_url(session)
    print(f"downloading {pdf_url}", file=sys.stderr)
    r = session.get(pdf_url, timeout=180)
    r.raise_for_status()
    DATA.mkdir(exist_ok=True)
    PDF_PATH.write_bytes(r.content)
    return PDF_PATH


def cluster_rows(words):
    """Group words sharing a page into visual row-bands by `top` proximity."""
    bands = []  # list of (band_top, [words])
    for w in sorted(words, key=lambda w: w["top"]):
        if bands and abs(w["top"] - bands[-1][0]) <= ROW_BAND_TOL:
            bands[-1][1].append(w)
            continue
        bands.append((w["top"], [w]))
    return bands


def page_column_bounds(words):
    """Locate the '(1)'..'(6)' header words and return their x0s as column starts."""
    markers = {}
    for w in words:
        m = re.fullmatch(r"\((\d)\)", w["text"])
        if m:
            markers[int(m.group(1))] = w["x0"]
    if len(markers) < 6:
        return None
    return [markers[i] for i in range(1, 7)]


def assign_column(x0, bounds):
    col = 0
    for i, b in enumerate(bounds):
        if x0 >= b - 2:
            col = i
    return col


def cadre_state_for_page(words, bounds):
    top_band = min((w["top"] for w in words if w["top"] < bounds[-1]), default=None)
    # cadre-state English name sits in the top-right corner, well above the "(1)" header row
    header_top = min(w["top"] for w in words if re.fullmatch(r"\(\d\)", w["text"]))
    candidates = [w for w in words if w["top"] < header_top - 5 and w["x0"] > bounds[3]]
    if not candidates:
        return None
    candidates.sort(key=lambda w: (w["top"], w["x0"]))
    return " ".join(w["text"] for w in candidates if re.search(r"[A-Za-z]", w["text"]))


def flush_record(rec_cols, cadre_state, allotment_year, sr_no):
    col_text = {i: " ".join(_rows_of(ws)) for i, ws in rec_cols.items()}
    # column 2: hindi name / english name / qualification, split by script + row order
    col2_rows = _rows_of(rec_cols.get(1, []))
    name_hi, name_en, qual_parts = "", "", []
    for row_text in col2_rows:
        if re.search(r"[ऀ-ॿ]", row_text) and not name_hi:
            # this PDF's font has a broken ToUnicode CMap for some conjunct glyphs
            # (renders as U+0000) — strip rather than store corrupt bytes
            name_hi = "".join(ch for ch in row_text if ch != "\x00")
        elif re.search(r"[A-Za-z]", row_text) and not name_en:
            name_en = row_text
        elif row_text.strip():
            qual_parts.append(row_text)
    qualification = " ".join(qual_parts).strip()

    # column 3: source code / officer code / domicile state (remaining rows)
    col3_rows = _rows_of(rec_cols.get(2, []))
    source, code, domicile_parts = "", "", []
    for row_text in col3_rows:
        tok = row_text.strip()
        if tok.upper() in SOURCE_CODES and not source:
            source = tok.upper()
        elif CODE_RE.match(tok) and not code:
            code = tok
        elif tok:
            domicile_parts.append(tok)
    domicile_state = " ".join(domicile_parts).strip()

    # column 4: dob / appointment date (occasional stray extra rows are ignored)
    col4_rows = _rows_of(rec_cols.get(3, []))
    dob, appt_date = "", ""
    for row_text in col4_rows:
        tok = row_text.strip()
        if DATE_RE.match(tok) and not dob:
            dob = tok
        elif DATE_RE.match(tok) and not appt_date:
            appt_date = tok

    # column 5: posting title (free text) + posting-effective date + pay scale, all in one cell
    col5_text = col_text.get(4, "")
    pay_m = re.search(r"Level\s+\S+(?:\s+[A-Z]\b)?", col5_text)
    pay_scale = pay_m.group(0) if pay_m else ""
    wef_m = re.search(r"\d{2}/\d{2}/\d{4}", col5_text)
    posting_wef = wef_m.group(0) if wef_m else ""
    current_posting = col5_text
    if pay_m:
        current_posting = current_posting.replace(pay_m.group(0), "")
    current_posting = re.sub(r"\d{2}/\d{2}/\d{4}", "", current_posting)
    current_posting = " ".join(current_posting.split())

    # column 6: awards/medals, free text
    awards = col_text.get(5, "")

    return {
        "cadre_state": cadre_state,
        "allotment_year": allotment_year,
        "sr_no": sr_no,
        "name_en": name_en,
        "name_hi": name_hi,
        "source_of_recruitment": source,
        "officer_code": code,
        "appointment_date": appt_date,
        "dob": dob,
        "qualification": qualification,
        "domicile_state": domicile_state,
        "pay_scale": pay_scale,
        "current_posting": current_posting,
        "posting_wef": posting_wef,
        "awards": awards,
    }


def _rows_of(band_words_list):
    """band_words_list: list of word-lists (one per row band) -> list of joined row texts."""
    return [" ".join(w["text"] for w in sorted(ws, key=lambda w: w["x0"])) for ws in band_words_list]


def parse_pdf(pdf_path):
    rows = []
    current_cadre = None
    current_year = ""
    rec_cols = {}       # column-index -> list of word-lists (one per row band in this record)
    rec_sr_no = None

    def flush():
        if rec_sr_no is not None:
            rows.append(flush_record(rec_cols, current_cadre, current_year, rec_sr_no))

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            words = page.extract_words(use_text_flow=False, keep_blank_chars=False)
            bounds = page_column_bounds(words)
            if not bounds:
                continue  # cover / TOC / appendix page, no data table
            cadre = cadre_state_for_page(words, bounds)
            if cadre:
                if cadre != current_cadre:
                    flush()
                    rec_cols, rec_sr_no = {}, None
                current_cadre = cadre

            header_top = min(w["top"] for w in words if re.fullmatch(r"\(\d\)", w["text"]))
            data_words = [w for w in words if w["top"] > header_top + 5]
            for band_top, band_words in cluster_rows(data_words):
                band_text = " ".join(w["text"] for w in sorted(band_words, key=lambda w: w["x0"]))
                ym = YEAR_HEADER_RE.search(band_text)
                if ym:
                    current_year = ym.group(1)
                    continue

                col0_words = [w for w in band_words if assign_column(w["x0"], bounds) == 0]
                sr_word = next((w for w in col0_words if w["text"].isdigit()), None)
                if sr_word:
                    flush()
                    rec_cols, rec_sr_no = {}, int(sr_word["text"])

                if rec_sr_no is None:
                    continue  # stray band before the first record on this page (rare)

                per_col = {}
                for w in band_words:
                    c = assign_column(w["x0"], bounds)
                    if c == 0:
                        continue
                    per_col.setdefault(c, []).append(w)
                for c, ws in per_col.items():
                    rec_cols.setdefault(c, []).append(ws)
        flush()

    return [r for r in rows if (r["name_en"] or r["name_hi"]) and r["cadre_state"] in VALID_CADRES]


def main():
    pdf_path = download_pdf(force="--force" in sys.argv)
    rows = parse_pdf(pdf_path)
    DATA.mkdir(exist_ok=True)
    with open(OUT, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(rows)
    by_cadre = {}
    for r in rows:
        by_cadre[r["cadre_state"]] = by_cadre.get(r["cadre_state"], 0) + 1
    for cadre, n in sorted(by_cadre.items()):
        print(f"{cadre}: {n} officers", file=sys.stderr)
    print(f"-> {OUT} ({len(rows)} officers)")


if __name__ == "__main__":
    main()
