#!/usr/bin/env python3
"""Classify each ministry/department website by publishing platform.

platform values:
  digifootprint-postpage  Next.js shell + /cms/wp-json custom "post-page" + "document" routes (MNRE, DoT, DPIIT)
  digifootprint-wpv2      Next.js shell + /cms/wp-json standard wp/v2 custom types (MeitY)
  wordpress               classic WordPress with /wp-json
  html                    server-rendered HTML (Drupal, NIC CMS, custom) — scrape pages
  js-shell                JavaScript shell with no API found yet
  dead / blocked          unreachable, or a bot challenge (not bypassed)
Writes data/fingerprint.csv. Polite: one request per second per host; hosts run in parallel.
"""
import csv, concurrent.futures as cf, json, re, ssl, sys, time, urllib.parse, urllib.request, http.cookiejar, os

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0 Safari/537.36"
CHALLENGE = re.compile(r"(?is)just a moment\.\.\.|challenge-platform|cf-chl-|client challenge|captcha|verify (?:that )?you(?:'| a)re")
HERE = os.path.dirname(os.path.abspath(__file__))
EXTRA = {"Finance (MoF)": "https://finmin.gov.in", "Planning (MoP)": "https://www.niti.gov.in"}


def get(op, url, last):
    wait = 1.0 - (time.time() - last[0])
    if wait > 0:
        time.sleep(wait)
    last[0] = time.time()
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "en"})
    try:
        with op.open(req, timeout=30) as r:
            return r.status, r.headers.get("Content-Type", ""), r.read(400000), r.geturl(), dict(r.headers)
    except urllib.error.HTTPError as e:
        return e.code, e.headers.get("Content-Type", ""), (e.read(4000) or b""), url, dict(e.headers)
    except Exception as e:
        return 0, "", str(e)[:200].encode(), url, {}


def text_len(raw):
    s = re.sub(rb"(?is)<(script|style|noscript)\b.*?</\1>", b" ", raw)
    return len(re.sub(rb"\s+", b" ", re.sub(rb"<[^>]+>", b" ", s)).strip())


def jsonish(raw):
    try:
        return json.loads(raw)
    except Exception:
        return None


def probe(row):
    site = row["website"] or EXTRA.get(row["name"], "")
    out = dict(row, website=site, final_url="", status="", platform="", api_base="", text_chars="", generator="", notes="")
    if not site:
        out["platform"] = "no-website"
        return out
    ctx = ssl.create_default_context()
    op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()),
                                     urllib.request.HTTPSHandler(context=ctx))
    last = [0.0]
    code, ct, raw, final, hdr = get(op, site, last)
    if code == 0 and b"CERTIFICATE" in raw.upper():
        op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()),
                                         urllib.request.HTTPSHandler(context=ssl._create_unverified_context()))
        out["notes"] += "bad-TLS-chain; "
        code, ct, raw, final, hdr = get(op, site, last)
    out.update(final_url=final, status=code, text_chars=text_len(raw))
    if code == 0:
        out.update(platform="dead", notes=out["notes"] + raw.decode("utf-8", "ignore")[:120])
        return out
    if CHALLENGE.search(raw[:200000].decode("utf-8", "ignore")):
        out["platform"] = "blocked"
        return out
    m = re.search(rb'<meta name="generator" content="([^"]+)"', raw, re.I)
    out["generator"] = m.group(1).decode("utf-8", "ignore")[:40] if m else ("Next.js" if b"/_next/static/" in raw else "")
    base = "{0.scheme}://{0.netloc}".format(urllib.parse.urlsplit(final))
    # shared ministry CMS
    c2, _, r2, _, _ = get(op, base + "/cms/wp-json/post-page/schemes_and_services?limit=1&page=1", last)
    j = jsonish(r2) if c2 == 200 else None
    if isinstance(j, dict) and "posts" in j:
        out.update(platform="digifootprint-postpage", api_base=base + "/cms/wp-json")
        return out
    c3, _, r3, _, _ = get(op, base + "/cms/wp-json/wp/v2/types", last)
    j = jsonish(r3) if c3 == 200 else None
    if isinstance(j, dict) and j:
        custom = [k for k in j if k not in ("post", "page", "attachment", "nav_menu_item", "wp_block", "wp_template",
                                            "wp_template_part", "wp_global_styles", "wp_navigation", "wp_font_family", "wp_font_face")]
        out.update(platform="digifootprint-wpv2", api_base=base + "/cms/wp-json", notes=out["notes"] + "types=" + ",".join(custom[:25]))
        return out
    c4, _, r4, _, _ = get(op, base + "/wp-json/", last)
    j = jsonish(r4) if c4 == 200 else None
    if isinstance(j, dict) and "namespaces" in j:
        out.update(platform="wordpress", api_base=base + "/wp-json")
        return out
    out["platform"] = "js-shell" if (int(out["text_chars"] or 0) < 600 or out["generator"] == "Next.js") else "html"
    return out


def main():
    rows = list(csv.DictReader(open(os.path.join(HERE, "..", "data", "targets.csv"))))
    with cf.ThreadPoolExecutor(8) as ex:
        res = list(ex.map(probe, rows))
    path = os.path.join(HERE, "..", "data", "fingerprint.csv")
    w = csv.DictWriter(open(path, "w"), fieldnames=list(res[0]))
    w.writeheader()
    w.writerows(res)
    for r in res:
        print(f"{r['platform']:24} {str(r['status']):4} {str(r['text_chars']):>6} {r['name'][:55]:55} {r['final_url'][:60]} {r['notes'][:80]}")


if __name__ == "__main__":
    main()
