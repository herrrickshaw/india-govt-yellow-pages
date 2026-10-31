#!/usr/bin/env python3
"""State-wise officers ↔ orders / notifications matrix (regional languages, OCR, translation).

The state counterpart of scripts/signatory_matrix.py. For each state / UT it

  targets   -> data/states/targets.csv          state-government departments with a website (from igod organizations_index)
  whoswho   -> data/states/state_officials.csv  who's-who rosters of those departments (reuses scripts/ministry_whoswho.py)
  crawl     -> ministry_documents/data/sites/<slug>/doc_links.csv   polite same-site crawl (reuses ministry_documents/tools/crawl_html.py)
  select    -> data/states/<ST>/candidates.csv  orders / GOs / notifications / circulars in English *and* the state language
  fetch     -> data/states/<ST>/pdf/            PDFs (gitignored; ~1 request/second per host)
  extract   -> data/states/<ST>/signatures.csv  signature block: Latin or Indic script; OCR in the state's language when scanned
  translate -> data/states/translations.json    names romanised + subject lines translated (Groq LLM, cached; rule-based fallback)
  match     -> data/states/<ST>/notification_signatories.csv   signatory -> roster officer (same matcher as the centre)
  matrix    -> data/states/<ST>/officer_topic_matrix.csv, SIGNATORY_MATRIX.md, and data/states/STATE_MATRIX.md (all states)

Run:   /usr/bin/python3 scripts/state_pipeline.py <stage|all> --states UP,TN,KL [--max-sites 20] [--max-pages 60] [--max-docs 300]
Needs: pdftotext/pdfinfo/pdftoppm, tesseract with the Indic language packs, `pip install --user indic_transliteration`,
       GROQ_API_KEY in ~/.config/market-secrets/credentials.env for translation (otherwise rule-based transliteration only).
"""
import argparse, csv, json, os, re, subprocess, sys, time, unicodedata
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from urllib.parse import urlparse

import pandas as pd

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))
import signatory_matrix as S  # noqa: E402  (shared extractor / matcher / report)

STATES_DIR = REPO / "data/states"
SITES = REPO / "ministry_documents/data/sites"
CRAWLER = REPO / "ministry_documents/tools/crawl_html.py"
TRANSLATIONS = STATES_DIR / "translations.json"

# state code -> (tesseract langs, unicode script name, indic_transliteration scheme, language)
STATE_LANG = {
    "UP": ("hin+eng", "DEVANAGARI", "hi", "Hindi"), "MP": ("hin+eng", "DEVANAGARI", "hi", "Hindi"),
    "BR": ("hin+eng", "DEVANAGARI", "hi", "Hindi"), "RJ": ("hin+eng", "DEVANAGARI", "hi", "Hindi"),
    "HR": ("hin+eng", "DEVANAGARI", "hi", "Hindi"), "HP": ("hin+eng", "DEVANAGARI", "hi", "Hindi"),
    "UK": ("hin+eng", "DEVANAGARI", "hi", "Hindi"), "CG": ("hin+eng", "DEVANAGARI", "hi", "Hindi"),
    "JH": ("hin+eng", "DEVANAGARI", "hi", "Hindi"), "DL": ("hin+eng", "DEVANAGARI", "hi", "Hindi"),
    "CH": ("pan+hin+eng", "GURMUKHI", "pa", "Punjabi"), "PB": ("pan+eng", "GURMUKHI", "pa", "Punjabi"),
    "MH": ("mar+hin+eng", "DEVANAGARI", "mr", "Marathi"), "GA": ("eng+mar", "DEVANAGARI", "mr", "English"),
    "GJ": ("guj+eng", "GUJARATI", "gu", "Gujarati"), "DD": ("guj+eng", "GUJARATI", "gu", "Gujarati"),
    "TN": ("tam+eng", "TAMIL", "ta", "Tamil"), "PY": ("tam+eng", "TAMIL", "ta", "Tamil"),
    "KL": ("mal+eng", "MALAYALAM", "ml", "Malayalam"), "LD": ("mal+eng", "MALAYALAM", "ml", "Malayalam"),
    "KA": ("kan+eng", "KANNADA", "kn", "Kannada"), "AP": ("tel+eng", "TELUGU", "te", "Telugu"),
    "TS": ("tel+eng", "TELUGU", "te", "Telugu"), "WB": ("ben+eng", "BENGALI", "bn", "Bengali"),
    "TR": ("ben+eng", "BENGALI", "bn", "Bengali"), "AN": ("eng+hin", "DEVANAGARI", "hi", "English"),
    "OD": ("ori+eng", "ORIYA", "or", "Odia"), "AS": ("asm+ben+eng", "BENGALI", "as", "Assamese"),
    "JK": ("eng+urd+hin", "DEVANAGARI", "hi", "English"), "LA": ("eng+urd", "DEVANAGARI", "hi", "English"),
    "MZ": ("eng", "LATIN", None, "English"), "ML": ("eng", "LATIN", None, "English"), "MN": ("eng+ben", "BENGALI", "bn", "English"),
    "NL": ("eng", "LATIN", None, "English"), "SK": ("eng", "LATIN", None, "English"), "AR": ("eng", "LATIN", None, "English"),
}
SCRIPT_RANGES = {"DEVANAGARI": (0x0900, 0x097F), "BENGALI": (0x0980, 0x09FF), "GURMUKHI": (0x0A00, 0x0A7F),
                 "GUJARATI": (0x0A80, 0x0AFF), "ORIYA": (0x0B00, 0x0B7F), "TAMIL": (0x0B80, 0x0BFF),
                 "TELUGU": (0x0C00, 0x0C7F), "KANNADA": (0x0C80, 0x0CFF), "MALAYALAM": (0x0D00, 0x0D7F)}

# document-type words in the state languages (orders, GOs, notifications, circulars, resolutions)
INDIC_DOC_WORDS = ["आदेश", "अधिसूचना", "शासनादेश", "परिपत्र", "ज्ञाप", "निर्देश", "नियम", "संकल्प", "शासन निर्णय", "परिपत्रक",
                   "અધિસૂચના", "ઠરાવ", "પરિપત્ર", "હુકમ", "அரசாணை", "ஆணை", "அறிவிக்கை", "சுற்றறிக்கை", "ഉത്തരവ്", "വിജ്ഞാപനം",
                   "സർക്കുലർ", "ಆದೇಶ", "ಅಧಿಸೂಚನೆ", "ಸುತ್ತೋಲೆ", "ఉత్తర్వు", "ప్రకటన", "సర్క్యులర్", "আদেশ", "বিজ্ঞপ্তি", "প্রজ্ঞাপন",
                   "ଆଦେଶ", "ବିଜ୍ଞପ୍ତି", "ਹੁਕਮ", "ਨੋਟੀਫਿਕੇਸ਼ਨ", "ਪੱਤਰ"]
LATIN_DOC_PAT = re.compile(S.DOC_PAT.pattern + r"|\bg\.?o\.?\b|\bgr\b|resolution|shasanadesh|adesh|aadesh|paripatra|circular", re.I)

# designation words (Indic) -> English, used to recognise a signature block and to label the signer
INDIC_DESIG = [
    ("अपर मुख्य सचिव", "Additional Chief Secretary"), ("प्रमुख सचिव", "Principal Secretary"), ("मुख्य सचिव", "Chief Secretary"),
    ("विशेष सचिव", "Special Secretary"), ("संयुक्त सचिव", "Joint Secretary"), ("उप सचिव", "Deputy Secretary"),
    ("अनु सचिव", "Under Secretary"), ("अनुसचिव", "Under Secretary"), ("अवर सचिव", "Under Secretary"), ("सचिव", "Secretary"),
    ("निदेशक", "Director"), ("आयुक्त", "Commissioner"), ("अनुभाग अधिकारी", "Section Officer"), ("सहायक", "Assistant"),
    ("कक्ष अधिकारी", "Section Officer"),
    ("અધિક મુખ્ય સચિવ", "Additional Chief Secretary"), ("અગ્ર સચિવ", "Principal Secretary"), ("સચિવ", "Secretary"),
    ("નાયબ સચિવ", "Deputy Secretary"), ("સંયુક્ત સચિવ", "Joint Secretary"), ("ઉપ સચિવ", "Deputy Secretary"), ("નિયામક", "Director"),
    ("முதன்மைச் செயலாளர்", "Principal Secretary"), ("கூடுதல் தலைமைச் செயலாளர்", "Additional Chief Secretary"),
    ("இணைச் செயலாளர்", "Joint Secretary"), ("துணைச் செயலாளர்", "Deputy Secretary"), ("செயலாளர்", "Secretary"),
    ("இயக்குநர்", "Director"), ("ஆணையர்", "Commissioner"),
    ("അഡീഷണൽ ചീഫ് സെക്രട്ടറി", "Additional Chief Secretary"), ("പ്രിൻസിപ്പൽ സെക്രട്ടറി", "Principal Secretary"),
    ("ജോയിന്റ് സെക്രട്ടറി", "Joint Secretary"), ("ഡെപ്യൂട്ടി സെക്രട്ടറി", "Deputy Secretary"), ("അണ്ടർ സെക്രട്ടറി", "Under Secretary"),
    ("സെക്രട്ടറി", "Secretary"), ("ഡയറക്ടർ", "Director"), ("കമ്മീഷണർ", "Commissioner"),
    ("ಪ್ರಧಾನ ಕಾರ್ಯದರ್ಶಿ", "Principal Secretary"), ("ಜಂಟಿ ಕಾರ್ಯದರ್ಶಿ", "Joint Secretary"), ("ಉಪ ಕಾರ್ಯದರ್ಶಿ", "Deputy Secretary"),
    ("ಅಧೀನ ಕಾರ್ಯದರ್ಶಿ", "Under Secretary"), ("ಕಾರ್ಯದರ್ಶಿ", "Secretary"), ("ನಿರ್ದೇಶಕ", "Director"), ("ಆಯುಕ್ತ", "Commissioner"),
    ("ముఖ్య కార్యదర్శి", "Chief Secretary"), ("కార్యదర్శి", "Secretary"), ("సంచాలకులు", "Director"), ("కమిషనర్", "Commissioner"),
    ("প্রধান সচিব", "Principal Secretary"), ("যুগ্ম সচিব", "Joint Secretary"), ("উপসচিব", "Deputy Secretary"), ("সচিব", "Secretary"),
    ("অধিকর্তা", "Director"), ("ପ୍ରମୁଖ ଶାସନ ସଚିବ", "Principal Secretary"), ("ସଚିବ", "Secretary"), ("ନିର୍ଦ୍ଦେଶକ", "Director"),
    ("ਪ੍ਰਮੁੱਖ ਸਕੱਤਰ", "Principal Secretary"), ("ਸਕੱਤਰ", "Secretary"), ("ਡਾਇਰੈਕਟਰ", "Director"),
]
INDIC_DESIG.sort(key=lambda x: -len(x[0]))
INDIC_HONORIFIC = re.compile(r"^(?:श्री|श्रीमती|डॉ\.?|डा\.?|सुश्री|કુ\.|શ્રી|શ્રીમતી|ડૉ\.?|திரு|திருமதி|டாக்டர்|ശ്രീ|ശ്രീമതി|ഡോ\.?|ಶ್ರೀ|ಶ್ರೀಮತಿ|ಡಾ\.?|శ్రీ|శ్రీమతి|డా\.?|শ্রী|শ্রীমতী|ডঃ|ଶ୍ରୀ|ଶ୍ରୀମତୀ|ਸ਼੍ਰੀ|ਸ਼੍ਰੀਮਤੀ|ਡਾ\.?)\s*")


def script_of(text):
    counts = {k: 0 for k in SCRIPT_RANGES}
    latin = 0
    for ch in text:
        o = ord(ch)
        if ch.isascii() and ch.isalpha():
            latin += 1; continue
        for k, (a, b) in SCRIPT_RANGES.items():
            if a <= o <= b:
                counts[k] += 1; break
    best = max(counts, key=counts.get)
    return (best if counts[best] > max(20, latin * 0.3) else "LATIN"), counts[best], latin


def indic_tokens(line, scr):
    a, b = SCRIPT_RANGES[scr]
    return [t for t in re.split(r"[\s,;:()\[\]/]+", line) if t and all(a <= ord(c) <= b or c in ".-'’" or 0x0964 <= ord(c) <= 0x0965 for c in t)]


INDIC_STOP = ["गार्ड", "बुक", "फाइल", "सेवा में", "आज्ञा से", "कार्यालय", "ज्ञाप", "प्रतिलिपि", "संख्या", "दिनांक", "विषय", "भवदीय",
              "अनुभाग", "शासन", "विभाग", "लखनऊ", "उत्तर प्रदेश", "आदेश", "अधिसूचना", "द्वारा", "तथा", "एवं", "निदेशक", "सचिव", "आयुक्त",
              "अधिकारी", "सूचना", "पत्र", "हस्ताक्षर", "मुहर", "पृष्ठ", "क्रमांक", "संलग्न", "प्रमाणित", "सही", "संबंध", "सम्बन्ध",
              "செய்யப்பட்டது", "வெளியிடப்படுகிறது", "அரசு", "ஆணை", "நகல்", "பெறுநர்", "அனுப்புநர்", "பொருள்", "நாள்", "பக்கம்",
              "ஆணையர்", "செயலாளர்", "இயக்குநர்", "துறை", "அலுவலகம்", "கையொப்பம்",
              "അനുസൃതമായിരിക്കും", "പകർപ്പ്", "സർക്കാർ", "ഉത്തരവ്", "വിഷയം", "തീയതി", "ഡയറക്ടർ", "സെക്രട്ടറി", "ജില്ലാ", "എല്ലാ",
              "ഓഫീസ്", "ഒപ്പ്", "നമ്പർ", "വകുപ്പ്", "പ്രിൻസിപ്പൽ", "ഗവർണറുടെ", "ഉത്തരവിൻ", "പ്രകാരം", "പകർപ", "ഉത്തരവ", "സർക്കുലർ",
              "प्रेषक", "अधिशासी", "अभियंता", "अभियन्ता", "अधीक्षण", "मुख्य", "उपरोक्त", "कृपया", "अवगत", "प्रतिलिपि", "निम्नलिखित",
              "ஒப்பம்", "ஆணைப்படி", "ஆளுநரின்", "நகல்", "மேற்கண்ட", "இணைப்பு"]


def find_signatories_indic(tail, scr):
    """Name line in the state script followed (within 3 lines) by a line with a known designation word."""
    if scr not in SCRIPT_RANGES:
        return []
    lines = [l.strip() for l in tail.splitlines()]
    out = []
    for i, line in enumerate(lines):
        if not line or len(line) > 70:
            continue
        core = INDIC_HONORIFIC.sub("", line.strip("()[] "))
        toks = indic_tokens(core, scr)
        if not (1 <= len(toks) <= 4) or len("".join(toks)) < 3 or len("".join(toks)) > 40:
            continue
        joined = " ".join(toks)
        if any(w in joined for w in INDIC_STOP) or joined.endswith("।") or joined.endswith("."):
            continue
        # the line itself must be (almost) only the name
        if len(re.sub(r"[\s()\[\].'’\-]", "", core)) > len("".join(toks)) + 2:
            continue
        for nxt in [l for l in lines[i + 1:i + 5] if l][:3]:
            hit = next(((w, en) for w, en in INDIC_DESIG if w in nxt), None)
            if hit and len(nxt) <= 90:
                out.append((" ".join(toks), nxt, hit[1], 3 + (2 if line.strip().startswith("(") else 0), i))
                break
    return out


def romanise_rule(name, scr):
    """Rule-based fallback: ITRANS transliteration normalised towards common Indian-English spellings."""
    try:
        from indic_transliteration import sanscript
        from indic_transliteration.sanscript import transliterate
        t = transliterate(name, getattr(sanscript, scr), sanscript.ITRANS)
    except Exception:
        return ""
    t = re.sub(r"[.|]", "", t)
    t = re.sub(r"a\b", "", t)                     # inherent short schwa at word end (not long A)
    t = re.sub(r"a(?=[^aeiouAEIOU\s]{1}[aeiouAEIOU])", "a", t)
    t = t.replace("Mh", "ngh").replace("~Nh", "ngh").replace("M", "n").replace("~N", "n").replace("~n", "n")
    t = t.replace("A", "a").replace("I", "i").replace("U", "u").replace("RRi", "ri").replace("R^i", "ri")
    t = t.replace("Sh", "sh").replace("S", "sh").replace("N", "n").replace("T", "t").replace("D", "d").replace("L", "l")
    t = re.sub(r"chh", "chh", t).replace("ee", "i").replace("oo", "u")
    t = re.sub(r"([bcdfghjklmnprstvyz])\1", r"\1", t)
    return " ".join(w.capitalize() for w in t.split())


# ------------------------------------------------------------------ Groq translation (cached)
def _groq_key():
    k = os.environ.get("GROQ_API_KEY")
    if k:
        return k
    p = Path.home() / ".config/market-secrets/credentials.env"
    if p.exists():
        m = re.search(r"^GROQ_API_KEY=(.+)$", p.read_text(), re.M)
        if m:
            return m.group(1).strip().strip('"')
    return None


GROQ_MODEL = "openai/gpt-oss-120b"


def groq_json(system, user, retries=5):
    import urllib.request
    key = _groq_key()
    if not key:
        return None
    body = json.dumps({"model": GROQ_MODEL, "temperature": 0, "response_format": {"type": "json_object"},
                       "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}]}).encode()
    for att in range(retries):
        try:
            req = urllib.request.Request("https://api.groq.com/openai/v1/chat/completions", data=body,
                                         headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json",
                                                  "User-Agent": "curl/8.7.1", "Accept": "application/json"})
            with urllib.request.urlopen(req, timeout=90) as r:
                d = json.load(r)
            return json.loads(d["choices"][0]["message"]["content"])
        except Exception as e:  # rate limit / transient
            err = e
            wait = 25 * (att + 1) if "429" in str(e) else 5 * (att + 1)
            time.sleep(wait)
    print(f"  groq failed: {err}", file=sys.stderr)
    return None


def load_cache():
    return json.loads(TRANSLATIONS.read_text()) if TRANSLATIONS.exists() else {"names": {}, "text": {}}


def save_cache(c):
    TRANSLATIONS.write_text(json.dumps(c, ensure_ascii=False, indent=0))


def translate_batch(cache, names, texts, language):
    """names: list of Indic-script personal names -> standard Latin spelling; texts: subject lines -> English."""
    names = [n for n in dict.fromkeys(names) if n and n not in cache["names"]]
    texts = [t for t in dict.fromkeys(texts) if t and t not in cache["text"]]
    sys_msg = (f"You process {language} text from Indian state government orders. Return JSON only: "
               '{"names": {"<original>": "<standard Latin spelling of this Indian personal name, honorifics removed>"}, '
               '"text": {"<original>": "<concise English translation>"}}. Keep keys exactly as given.')
    for i in range(0, max(len(names), len(texts)), 12):
        chunk_n, chunk_t = names[i:i + 12], texts[i:i + 12]
        if not chunk_n and not chunk_t:
            continue
        res = groq_json(sys_msg, json.dumps({"names": chunk_n, "text": chunk_t}, ensure_ascii=False))
        if res:
            cache["names"].update({k: v for k, v in (res.get("names") or {}).items() if k in chunk_n})
            cache["text"].update({k: v for k, v in (res.get("text") or {}).items() if k in chunk_t})
            save_cache(cache)
        time.sleep(2.5)  # free-tier politeness
    return cache


# ------------------------------------------------------------------ stages
def sdir(st):
    d = STATES_DIR / st; (d / "pdf").mkdir(parents=True, exist_ok=True); return d


def slug_for(website):
    host = urlparse(website).netloc.lower()
    return "st-" + re.sub(r"^www\.|\.gov\.in$|\.nic\.in$|\.org\.in$|\.in$", "", host).replace(".", "-")


def targets(args):
    d = pd.read_csv(REPO / "data/organizations_index.csv", low_memory=False)
    sg = d[(d.branch == "sg") & d.website.notna()].copy()
    sg = sg[sg.state.isin(args.states)] if args.states else sg
    sg = sg.drop_duplicates("website")
    sg["slug"] = sg.website.map(slug_for)
    # secretariat departments first (they issue the GOs), then directorates / boards
    sec = sg.name.str.contains(r"department|secretariat|directorate|commissionerate", case=False)
    sg = pd.concat([sg[sec], sg[~sec]])
    if args.max_sites:
        sg = sg.groupby("state", group_keys=False).head(args.max_sites)
    out = sg[["state", "name", "website", "igod_org_id", "category_code", "slug"]]
    STATES_DIR.mkdir(exist_ok=True)
    prev = STATES_DIR / "targets.csv"
    if prev.exists():
        old = pd.read_csv(prev)
        out = pd.concat([old[~old.state.isin(out.state.unique())], out])
    out.to_csv(prev, index=False)
    print(f"targets: {len(out)} department sites, states {sorted(out.state.unique())}")


def whoswho(args):
    import ministry_whoswho as W
    import requests
    requests.packages.urllib3.disable_warnings()
    # state sites name the page differently from union ministries
    W.PROBE_PATHS = list(dict.fromkeys(W.PROBE_PATHS + [
        "/en/whos-who", "/en/whos-who/", "/whos-who/", "/who-is-who", "/whoswho", "/en/who-is-who", "/officers", "/officials",
        "/key-officials", "/key-officers", "/our-officers", "/officers-list", "/directory", "/telephone-directory",
        "/contact-us", "/contact", "/contacts", "/staff", "/staff-directory", "/organisation", "/organization",
        "/administration", "/about-us/officers", "/about-us/organisation", "/about/whos-who", "/about-us/contact-us",
        "/en/contact-us", "/en/officers", "/Pages/whos-who.aspx", "/Page/WhosWho.aspx", "/whos-who.aspx", "/en/directory",
        "/officers-directory", "/en/key-officials", "/secretariat", "/en/administration"]))
    W.WHO_RE = re.compile(r"who[\s_'’%2-]*(i?s)?[\s_'’%27-]*who|officers?\b|officials|directory|key[- ]official", re.I)
    t = pd.read_csv(STATES_DIR / "targets.csv")
    t = t[t.state.isin(args.states)] if args.states else t
    out_path = STATES_DIR / "state_officials.csv"
    done = set()
    if out_path.exists():
        prev = pd.read_csv(out_path)
        done = set(prev[prev.name.notna() & (prev.name.astype(str).str.strip() != "")].website)
        prev[prev.website.isin(done)].to_csv(out_path, index=False)   # drop empty placeholders so they are rescanned
    rows = [r for r in t.to_dict("records") if r["website"] not in done]
    print(f"whoswho: {len(rows)} sites to scan ({len(done)} done)")
    results = []

    def job(r):
        try:
            name, website, used, offs = W.scrape_ministry({"name": r["name"], "website": r["website"], "igod_org_id": r["igod_org_id"] or ""})
        except Exception as e:  # noqa
            return r, "", [], str(e)[:100]
        return r, used, offs, ""

    with ThreadPoolExecutor(max_workers=8) as ex:
        for i, (r, used, offs, err) in enumerate(ex.map(job, rows), 1):
            print(f"  [{i}/{len(rows)}] {r['state']} {r['name'][:50]}: {len(offs)} {'(' + used + ')' if used else err or '(no whos-who)'}")
            for o in offs:
                results.append({"state": r["state"], "department": r["name"], "website": r["website"],
                                "name": o.get("name", ""), "designation": o.get("designation", ""), "division": o.get("division", ""),
                                "room": o.get("room", ""), "phones": "; ".join(o.get("phones") or []) if isinstance(o.get("phones"), list) else o.get("phones", ""),
                                "email": o.get("email", ""), "source_url": used})
            if not offs:
                results.append({"state": r["state"], "department": r["name"], "website": r["website"], "name": "", "designation": "",
                                "division": "", "room": "", "phones": "", "email": "", "source_url": used or f"(none: {err})"})
    df = pd.DataFrame(results)
    if out_path.exists():
        df = pd.concat([pd.read_csv(out_path), df], ignore_index=True)
    df.to_csv(out_path, index=False)
    real = df[df.name.astype(str).str.strip() != ""]
    print(f"whoswho: {len(real)} officers across {real.department.nunique()} departments -> {out_path}")


def crawl(args):
    t = pd.read_csv(STATES_DIR / "targets.csv")
    t = t[t.state.isin(args.states)] if args.states else t
    jobs = [(r.website, r.slug) for r in t.itertuples() if not (SITES / r.slug / "doc_links.csv").exists()]
    print(f"crawl: {len(jobs)} sites (max {args.max_pages} pages each), {len(t) - len(jobs)} already crawled")
    (REPO / "ministry_documents/logs").mkdir(exist_ok=True)

    def run(job):
        website, slug = job
        log = open(REPO / "ministry_documents/logs" / f"{slug}.log", "w")
        subprocess.run(["/usr/bin/python3", str(CRAWLER), website, slug, "--max-pages", str(args.max_pages)], stdout=log, stderr=log, timeout=3600)
        n = sum(1 for _ in open(SITES / slug / "doc_links.csv")) - 1 if (SITES / slug / "doc_links.csv").exists() else -1
        return slug, n

    with ThreadPoolExecutor(max_workers=8) as ex:
        for slug, n in ex.map(run, jobs):
            print(f"  {slug}: {n} document links")


def select(args):
    t = pd.read_csv(STATES_DIR / "targets.csv")
    for st in args.states or sorted(t.state.unique()):
        rows = []
        for r in t[t.state == st].itertuples():
            p = SITES / r.slug / "doc_links.csv"
            if not p.exists():
                continue
            d = pd.read_csv(p)
            d["ministry"] = r.name; d["website"] = r.website
            rows.append(d)
        if not rows:
            print(f"select {st}: nothing crawled"); continue
        d = pd.concat(rows, ignore_index=True)
        d["title"] = d.text.fillna("").astype(str).str.strip()
        blob = (d.title + " " + d.url.fillna("")).str.lower()
        indic = d.title.map(lambda x: any(w in x for w in INDIC_DOC_WORDS))
        cand = d[(blob.str.contains(LATIN_DOC_PAT) | indic) & d.url.str.lower().str.contains(r"\.pdf")].drop_duplicates("url").copy()
        cand.insert(0, "doc_id", cand.url.map(S.doc_id))
        cand["host"] = cand.url.map(lambda u: urlparse(u).netloc)
        cand["group"] = st; cand["category"] = ""; cand["date"] = ""
        if args.max_docs:
            cand = cand.groupby("ministry", group_keys=False).head(max(5, args.max_docs // max(1, cand.ministry.nunique()) + 5)).head(args.max_docs)
        cand[["doc_id", "ministry", "title", "group", "category", "date", "url", "host", "website", "found_on"]].to_csv(sdir(st) / "candidates.csv", index=False)
        print(f"select {st}: {len(cand)} candidate PDFs from {len(d)} links ({cand.ministry.nunique()} departments)")


def _bind(st):
    S.OUT = sdir(st); S.PDF = S.OUT / "pdf"; S.OCR_LANG = STATE_LANG.get(st, ("eng",))[0]


def fetch(args):
    for st in args.states:
        _bind(st); print(f"[{st}]"); S.fetch()


def extract(args):
    for st in args.states:
        _bind(st)
        langs, scr, _, language = STATE_LANG.get(st, ("eng", "LATIN", None, "English"))
        cand = pd.read_csv(S.OUT / "candidates.csv").set_index("doc_id")
        rows = []
        files = sorted(S.PDF.glob("*.pdf"))
        print(f"[{st}] extract: {len(files)} PDFs, OCR {langs}")
        for k, f in enumerate(files):
            if f.stem not in cand.index:
                continue
            n, head, tail = S.pdf_text(f)
            ocr_used = S.pdf_text.last_ocr
            doc_scr, n_ind, n_lat = script_of(head + tail)
            subj = S.SUBJECT.search(head)
            subj = re.sub(r"\s+", " ", subj.group(1)).strip()[:300] if subj else ""
            if not subj:  # first substantive line as a stand-in subject
                for l in head.splitlines():
                    l = l.strip()
                    if len(l) > 25 and not re.search(r"\d{5,}", l):
                        subj = l[:200]; break
            base = dict(doc_id=f.stem, pages=n, script=doc_scr, indic_chars=n_ind, latin_chars=n_lat, ocr=int(ocr_used),
                        scanned=int(len(re.sub(r"\s", "", head)) < 80), subject_raw=subj, file_number="")
            lat = S.find_signatories(tail)
            ind = find_signatories_indic(tail, doc_scr if doc_scr != "LATIN" else scr)
            sigs = [(nm, dg, dg, "LATIN", stv, i) for nm, dg, stv, i in lat] + [(nm, dg, en, doc_scr, stv, i) for nm, dg, en, stv, i in ind]
            dsig = S.digital_signer(tail) or S.digital_signer(head)
            if not sigs and dsig and len(dsig.split()) >= 2 and not S.STOP_NAME.search(dsig):
                sigs = [(dsig, "(digital signature only)", "(digital signature only)", "LATIN", 2, 0)]
            if not sigs:
                rows.append({**base, "sig_rank": 0, "signatory_raw": "", "signatory": "", "sig_script": "", "sig_designation_raw": "", "sig_designation": "", "strength": 0})
            for rnk, (nm, dg, en, sscr, stv, _) in enumerate(sorted(sigs, key=lambda x: -x[5])[:3], 1):
                rows.append({**base, "sig_rank": rnk, "signatory_raw": nm, "signatory": nm if sscr == "LATIN" else "",
                             "sig_script": sscr, "sig_designation_raw": dg, "sig_designation": en, "strength": stv})
            if (k + 1) % 100 == 0:
                print(f"  {k+1}/{len(files)}")
        df = pd.DataFrame(rows)
        df.to_csv(S.OUT / "signatures.csv", index=False)
        d1 = df.drop_duplicates("doc_id")
        print(f"[{st}] extract: {len(d1)} docs; script mix {d1.script.value_counts().to_dict()}; with signature "
              f"{(d1.sig_rank > 0).sum()} (Indic-script names {(df.sig_script.isin(SCRIPT_RANGES)).sum()}); OCR used {d1.ocr.sum()}")


def translate(args):
    cache = load_cache()
    for st in args.states:
        _bind(st)
        langs, scr, _, language = STATE_LANG.get(st, ("eng", "LATIN", None, "English"))
        p = S.OUT / "signatures.csv"
        if not p.exists():
            continue
        df = pd.read_csv(p)
        names = df[df.sig_script.isin(SCRIPT_RANGES)].signatory_raw.dropna().astype(str).tolist()
        need_tr = df.subject_raw.fillna("").map(lambda x: script_of(x)[0] != "LATIN")
        texts = df[need_tr].subject_raw.astype(str).tolist()
        print(f"[{st}] translate: {len(set(names))} names, {len(set(texts))} subject lines ({language})")
        if _groq_key():
            cache = translate_batch(cache, names, texts, language)
        else:
            print("  no GROQ_API_KEY: rule-based transliteration only, subjects untranslated")
        def latin(row):
            if row.sig_script in SCRIPT_RANGES:
                return cache["names"].get(str(row.signatory_raw)) or romanise_rule(str(row.signatory_raw), row.sig_script)
            return row.signatory
        df["signatory"] = df.apply(latin, axis=1)
        df["signatory_rule"] = df.apply(lambda r: romanise_rule(str(r.signatory_raw), r.sig_script) if r.sig_script in SCRIPT_RANGES else "", axis=1)
        df["subject"] = [cache["text"].get(str(t), t) if nt else t for t, nt in zip(df.subject_raw.fillna(""), need_tr)]
        df["subject_language"] = ["en" if not nt else language for nt in need_tr]
        df.to_csv(p, index=False)
        print(f"  romanised {df.signatory.ne('').sum() - (df.sig_script == 'LATIN').sum()} Indic names; translated {sum(1 for t in set(texts) if t in cache['text'])}/{len(set(texts))} subjects")


# igod state code -> DoPT cadre code (AGMUT cadre = 'UT' covers Arunachal, Goa, Mizoram and all UTs)
CADRE = {"KA": "KN", "BR": "BH", "AS": "AM", "HR": "HY", "TS": "TG", "UK": "UD", "DL": "UT", "JK": "UT", "CH": "UT", "PY": "UT",
         "AN": "UT", "LA": "UT", "LD": "UT", "DD": "UT", "AR": "UT", "GA": "UT", "MZ": "UT"}


def state_rosters(st):
    R = []
    p = STATES_DIR / "state_officials.csv"
    if p.exists():
        so = pd.read_csv(p)
        so = so[(so.state == st) & so.name.notna() & (so.name.astype(str).str.strip() != "")]
        for r in so.itertuples():
            R.append(dict(roster="state_whoswho", ministry=r.department, name=r.name, designation=r.designation if isinstance(r.designation, str) else "",
                          division=r.division if isinstance(r.division, str) else "", email=r.email if isinstance(r.email, str) else "",
                          phones=r.phones if isinstance(r.phones, str) else "", source_url=r.source_url))
    for fn, tag in (("ias_officers.csv", "ias_civil_list"), ("ips_officers.csv", "ips_civil_list")):
        q = REPO / "data" / fn
        if q.exists():
            c = pd.read_csv(q, low_memory=False)
            col = next((x for x in ("cadre_code", "cadre", "cadre_state") if x in c.columns), None)
            if col is None:
                continue
            want = CADRE.get(st, st)
            cv = c[col].astype(str).str.upper().str.strip()
            c = c[(cv == want) | cv.str.startswith(want + " ") | cv.str.contains(rf"\b{want}\b")]
            for r in c.itertuples():
                R.append(dict(roster=tag, ministry=str(getattr(r, "current_posting", "") or ""), name=r.name_en,
                              designation=str(getattr(r, "current_posting", "") or ""), division="", email="", phones="",
                              source_url=str(getattr(r, "er_sheet_url", "") or "")))
    df = pd.DataFrame(R)
    if df.empty:
        return df
    df["name_clean"] = df.name.astype(str).map(S.clean_name)
    df = df[~df.name_clean.str.fullmatch(r"-+|\.*|nil|vacant", case=False)]
    import hashlib
    df["officer_id"] = df.apply(lambda r: hashlib.sha1(f"{r.roster}|{r.ministry}|{r.name_clean}|{r.designation}".encode()).hexdigest()[:10], axis=1)
    return df.reset_index(drop=True)


def match(args):
    S.CENTRAL = re.compile(".")  # in a state, the civil-list posting is the state posting
    S.ministry_key = lambda _s: {"_same_state"}   # every roster entry is the same state government
    for st in args.states:
        _bind(st)
        ros = state_rosters(st)
        if ros.empty or not (S.OUT / "signatures.csv").exists():
            print(f"[{st}] match: no roster or no signatures"); continue
        S.load_rosters = lambda ros=ros: ros
        sig = pd.read_csv(S.OUT / "signatures.csv")
        sig = sig[sig.signatory.fillna("") != ""] if "signatory" in sig else sig
        sig.to_csv(S.OUT / "signatures.csv", index=False)
        print(f"[{st}] match: roster {len(ros)} ({ros.roster.value_counts().to_dict()})")
        S.match()


def matrix(args):
    parts = []
    for st in args.states:
        _bind(st)
        if not (S.OUT / "notification_signatories.csv").exists():
            continue
        S.matrix()
        md = (S.OUT / "SIGNATORY_MATRIX.md").read_text().replace("# Who signed what", f"# {st} — who signed what", 1)
        (S.OUT / "SIGNATORY_MATRIX.md").write_text(md)
        ns = pd.read_csv(S.OUT / "notification_signatories.csv"); ns.insert(0, "state", st); parts.append(ns)
    if parts:
        allns = pd.concat(parts, ignore_index=True)
        allns.to_csv(STATES_DIR / "notification_signatories_all_states.csv", index=False)
        lines = ["# State-wise officers ↔ orders matrix — overview\n", f"_Built {time.strftime('%Y-%m-%d')} by `scripts/state_pipeline.py`._\n",
                 "| State | candidates | fetched | signature found | matched docs | officers linked | Indic-script signatures | per-state report |", "|---|---|---|---|---|---|---|---|"]
        for st in args.states:
            d = sdir(st)
            if not (d / "candidates.csv").exists():
                continue
            c = pd.read_csv(d / "candidates.csv"); f = len(list((d / "pdf").glob("*.pdf")))
            s = pd.read_csv(d / "signatures.csv") if (d / "signatures.csv").exists() else pd.DataFrame()
            n = allns[allns.state == st]
            lines.append(f"| {st} ({STATE_LANG.get(st, ('', '', '', 'English'))[3]}) | {len(c)} | {f} | {s[s.sig_rank > 0].doc_id.nunique() if len(s) else 0} | "
                         f"{n[n.match_status == 'matched'].doc_id.nunique()} | {n[n.match_status == 'matched'].officer_id.nunique()} | "
                         f"{int(s.sig_script.isin(SCRIPT_RANGES).sum()) if len(s) else 0} | [{st}/SIGNATORY_MATRIX.md]({st}/SIGNATORY_MATRIX.md) |")
        (STATES_DIR / "STATE_MATRIX.md").write_text("\n".join(lines) + "\n")
        print(f"matrix: wrote {STATES_DIR / 'STATE_MATRIX.md'}")


STAGES = ["targets", "whoswho", "crawl", "select", "fetch", "extract", "translate", "match", "matrix"]

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("stages", nargs="+")
    ap.add_argument("--states", default="", help="comma-separated state codes, e.g. UP,TN,KL")
    ap.add_argument("--max-sites", type=int, default=0)
    ap.add_argument("--max-pages", type=int, default=60)
    ap.add_argument("--max-docs", type=int, default=300)
    a = ap.parse_args()
    a.states = [s.strip().upper() for s in a.states.split(",") if s.strip()]
    stages = STAGES if a.stages == ["all"] else a.stages
    for s in stages:
        globals()[s](a)
