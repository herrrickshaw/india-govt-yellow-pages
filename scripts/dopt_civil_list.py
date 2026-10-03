#!/usr/bin/env python3
"""IAS e-Civil List (DoPT) — one officer per row, all 26 cadres.

iascivillist.dopt.gov.in needs no session/CSRF: POST ViewCadreCode=<code>
to /Home/ViewList returns that cadre's full officer table in one page,
each <tr> carrying a base64-embedded photo we strip before parsing.

Output: data/ias_officers.csv
"""
import csv
import html
import re
import sys
import time
from pathlib import Path

import requests

BASE = "https://iascivillist.dopt.gov.in/Home/ViewList"
DATA = Path(__file__).resolve().parent.parent / "data"
OUT = DATA / "ias_officers.csv"
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0 Safari/537.36")
DELAY = 1.0

CADRES = [
    "UT", "AP", "AM", "BH", "CG", "GJ", "HY", "HP", "JH", "KN", "KL", "MP",
    "MH", "MN", "NL", "OD", "PB", "RJ", "SK", "TN", "TG", "TR", "UP", "UD", "WB",
]

FIELDS = [
    "cadre_code", "sr_no", "name_en", "name_hi", "identity_no", "allotment_year",
    "source_of_recruitment", "qualification", "pay_scale", "remarks",
    "domicile_state", "current_posting", "posting_wef", "dob", "er_sheet_url",
]

session = requests.Session()
session.headers.update({"User-Agent": UA})

IMG_RE = re.compile(r'src="data:image/[^"]*"')


def strip_images(row_html):
    return IMG_RE.sub('src=""', row_html)


def clean(s):
    s = re.sub(r"<[^>]+>", " ", s or "")
    return " ".join(html.unescape(s).split())


def parse_row(row_html, cadre_code, sr_no):
    row_html = strip_images(row_html)

    dob_m = re.search(r"DOB:\s*([\d/]+)", row_html)
    href_m = re.search(r'<a href="([^"]+)"[^>]*><b>Name:</b>', row_html)
    name_m = re.search(r"<b>Name:</b>\s*([^<]+)</a>", row_html)
    name_hi_m = re.search(r"<h3>([^<]*)</h3>", row_html)
    id_m = re.search(r"<b>Identity No\.:</b>\s*([^<]+)", row_html)
    year_m = re.search(r"<b>Allotment Year:</b>\s*([^<]+)", row_html)
    src_m = re.search(r"<b>Source of Recruitment:</b>\s*([^<]+)", row_html)
    qual_m = re.search(r"<b>Qualification\(Subject\):</b>(.*?)</p>", row_html, re.S)
    pay_m = re.search(r"<b>Pay Scale:</b>\s*([^<]+)", row_html)
    remarks_m = re.search(r"<b>Remarks:</b>\s*([^<]*)", row_html)
    domicile_m = re.search(r"<b>&</b>\s*([^<]+)", row_html)
    posting_block_m = re.search(r"<b>Posting:-</b>.*?<li>(.*?)</li>", row_html, re.S)

    posting_text, posting_wef = "", ""
    if posting_block_m:
        block = posting_block_m.group(1)
        wef_m = re.search(r"Posting W\.E\.F\.:\s*([\d/]*)", block)
        posting_wef = wef_m.group(1) if wef_m else ""
        posting_text = clean(re.sub(r"Posting W\.E\.F\.:\s*[\d/]*", "", block))

    return {
        "cadre_code": cadre_code,
        "sr_no": sr_no,
        "name_en": clean(name_m.group(1)) if name_m else "",
        "name_hi": clean(name_hi_m.group(1)) if name_hi_m else "",
        "identity_no": clean(id_m.group(1)) if id_m else "",
        "allotment_year": clean(year_m.group(1)) if year_m else "",
        "source_of_recruitment": clean(src_m.group(1)) if src_m else "",
        "qualification": clean(qual_m.group(1)) if qual_m else "",
        "pay_scale": clean(pay_m.group(1)) if pay_m else "",
        "remarks": clean(remarks_m.group(1)) if remarks_m else "",
        "domicile_state": clean(domicile_m.group(1)) if domicile_m else "",
        "current_posting": posting_text,
        "posting_wef": posting_wef,
        "dob": dob_m.group(1) if dob_m else "",
        "er_sheet_url": html.unescape(href_m.group(1)) if href_m else "",
    }


def fetch_cadre(cadre_code):
    for attempt in range(3):
        try:
            r = session.post(BASE, data={"ViewCadreCode": cadre_code, "btn_submit": "Submit"}, timeout=120)
            if r.status_code == 200:
                return r.text
        except requests.RequestException as e:
            print(f"  retry {attempt+1} {cadre_code}: {e}", file=sys.stderr)
        time.sleep(2 * (attempt + 1))
    return None


def main():
    rows = []
    for cadre_code in CADRES:
        html_text = fetch_cadre(cadre_code)
        if not html_text:
            print(f"FAILED cadre {cadre_code}", file=sys.stderr)
            continue
        trs = re.findall(r"<tr>(.*?)</tr>", html_text, re.S)
        n = 0
        for tr in trs[1:]:  # skip header row
            if "Identity No" not in tr:
                continue
            rec = parse_row(tr, cadre_code, len(rows) + 1)
            if rec["name_en"]:
                rows.append(rec)
                n += 1
        print(f"{cadre_code}: {n} officers", file=sys.stderr)
        time.sleep(DELAY)

    DATA.mkdir(exist_ok=True)
    with open(OUT, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(rows)
    print(f"-> {OUT} ({len(rows)} officers)")


if __name__ == "__main__":
    main()
