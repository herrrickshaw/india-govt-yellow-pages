#!/usr/bin/env python3
"""Extract metadata from ministry sites on the shared "digifootprint" CMS (Next.js + /cms/wp-json post-page API).

Per site, writes data/sites/<slug>/:
  files.csv        every uploaded file record (central_documents): id, title, date, language, pdf_type, url, size, mime
  documents.jsonl  every document listing entry with its category path and the file ids it references
  content/<type>.jsonl  other post types (schemes_and_services, our_division, tenders_post, ...)
  summary.json     counts, endpoints that worked, errors
Endpoints were found by capturing the MNRE site's own network calls (2026-10-26):
  post-page/central_documents?limit=&page=     bulk file registry, acf_data.pdf.url = direct PDF link
  taxonomy/documents_category                   category tree
  document/documents?document_category=<slug>&limit=&page=&sort=acf&order=DESC
  post-page/<type>?limit=&page=                 other content types
Read-only GETs, one request per second per host. No keys or credentials are used.
Usage: extract_postpage.py <api_base> <slug> [--max-pages N]
"""
import csv, json, os, sys, time, urllib.parse, urllib.request, http.cookiejar, ssl

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0 Safari/537.36"
HERE = os.path.dirname(os.path.abspath(__file__))
TYPES = ["schemes_and_services", "our_division", "our_organisation", "our_team", "tenders_post", "careers_post",
         "initiatives", "international_collaboration", "call_for_proposals", "competition_awards", "photos_post",
         "videos_post", "infographic", "important_initiative", "in-spotlight", "directory_post", "parliament_questions",
         "citizen_engagement", "grievance_redressal", "about_us", "our_performance", "our_departments", "brochures_post",
         "presentation", "swipe_card_panel", "top_banner", "persona_cards", "important_links", "whats_new"]
LIMIT = 100


class Client:
    def __init__(self, base):
        self.base = base.rstrip("/")
        self.op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()),
                                              urllib.request.HTTPSHandler(context=ssl.create_default_context()))
        self.last = 0.0
        self.calls = 0

    def get(self, path, tries=3):
        url = f"{self.base}/{path}"
        for attempt in range(tries):
            wait = 1.0 - (time.time() - self.last)
            if wait > 0:
                time.sleep(wait)
            self.last = time.time()
            self.calls += 1
            try:
                req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
                with self.op.open(req, timeout=60) as r:
                    return json.loads(r.read())
            except urllib.error.HTTPError as e:
                if e.code in (502, 503, 504) and attempt < tries - 1:
                    time.sleep(10 * (attempt + 1))
                    continue
                return {"_error": e.code}
            except Exception as e:
                if attempt < tries - 1:
                    time.sleep(10 * (attempt + 1))
                    continue
                return {"_error": str(e)[:120]}


def pages(cl, path, max_pages):
    """Yield posts from a {"posts", "total_pages"} paged endpoint."""
    sep = "&" if "?" in path else "?"
    page, total = 1, 1
    while page <= min(total, max_pages):
        d = cl.get(f"{path}{sep}limit={LIMIT}&page={page}")
        if not isinstance(d, dict) or "_error" in d:
            yield {"_error": d.get("_error") if isinstance(d, dict) else "bad", "_page": page}
            if total > 1:  # page count known: skip the bad page (DPIIT 500s on one page of 159) and go on
                page += 1
                continue
            return
        posts = d.get("posts") or []
        if isinstance(posts, dict):
            posts = [posts]
        yield from posts
        total = int(d.get("total_pages") or 1)
        page += 1


def main():
    base, slug = sys.argv[1], sys.argv[2]
    max_pages = int(sys.argv[sys.argv.index("--max-pages") + 1]) if "--max-pages" in sys.argv else 400
    out = os.path.join(HERE, "..", "data", "sites", slug)
    os.makedirs(os.path.join(out, "content"), exist_ok=True)
    cl = Client(base)
    summary = {"api_base": base, "slug": slug, "started": time.strftime("%Y-%m-%dT%H:%M:%S"), "errors": [], "types": {}}

    # 1. bulk file registry
    n = 0
    # write to .tmp and rename at the end: in Dropbox-synced ~/Downloads, long-open files were swapped for empty ones
    with open(os.path.join(out, "files.csv.tmp"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["file_id", "title", "file_date", "post_date", "language", "pdf_type", "url", "size", "mime", "hindi_url"])
        for p in pages(cl, "post-page/central_documents", max_pages):
            if "_error" in p:
                summary["errors"].append({"central_documents": p}); continue
            a = p.get("acf_data") or {}
            # the file field is named pdf, pdf_both, pdf_english, ... per site: take the first that carries a url
            withurl = [v for v in a.values() if isinstance(v, dict) and v.get("url")]
            pdf = withurl[0] if withurl else {}
            hin = withurl[1] if len(withurl) > 1 else {}
            w.writerow([p.get("ID"), (a.get("title") or p.get("post_title") or "").strip(), a.get("file_date", ""),
                        p.get("post_date", ""), ",".join(a.get("language") or []) if isinstance(a.get("language"), list) else a.get("language", ""),
                        a.get("pdf_type", ""), pdf.get("url", ""), pdf.get("filesize", ""), pdf.get("mime_type", ""), hin.get("url", "")])
            n += 1
    os.replace(os.path.join(out, "files.csv.tmp"), os.path.join(out, "files.csv"))
    summary["files"] = n

    # 2. document listings by category
    tax = cl.get("taxonomy/documents_category")
    cats = (tax or {}).get("documents_category") or [] if isinstance(tax, dict) else []
    json.dump(cats, open(os.path.join(out, "categories.json"), "w"), ensure_ascii=False, indent=1)
    seen, nd = set(), 0
    with open(os.path.join(out, "documents.jsonl"), "w") as f:
        for c in sorted(cats, key=lambda c: (c.get("parent", 0) != 0, -int(c.get("count") or 0))):
            if not int(c.get("count") or 0):
                continue
            q = f"document/documents?document_category={urllib.parse.quote(c['slug'])}&sort=acf&order=DESC&search="
            for p in pages(cl, q, max_pages):
                if "_error" in p:
                    summary["errors"].append({"documents": c["slug"], **p}); continue
                if p.get("ID") in seen:
                    continue
                seen.add(p.get("ID"))
                a = p.get("acf_data") or {}
                files = []
                for e in a.get("file") or []:
                    if not isinstance(e, dict):
                        continue
                    ids = e.get("file") if isinstance(e.get("file"), list) else ([e["file"]] if isinstance(e.get("file"), int) else [])
                    files.append({"type": e.get("type"), "title": e.get("title"), "external_link": e.get("external_link"), "file_ids": ids})
                rec = {"id": p.get("ID"), "title": (a.get("title") or p.get("post_title") or "").strip(), "date": a.get("date") or "",
                       "post_date": p.get("post_date"), "modified": p.get("post_modified"), "slug": p.get("post_name"),
                       "categories": [x.get("slug") for x in p.get("documents_category") or []], "files": files}
                f.write(json.dumps(rec, ensure_ascii=False) + "\n")
                nd += 1
    summary["documents"] = nd

    # 3. other content types
    for t in TYPES:
        k = 0
        with open(os.path.join(out, "content", f"{t}.jsonl"), "w") as f:
            for p in pages(cl, f"post-page/{t}", max_pages):
                if "_error" in p:
                    break
                f.write(json.dumps({"id": p.get("ID"), "title": p.get("post_title"), "date": p.get("post_date"),
                                    "modified": p.get("post_modified"), "slug": p.get("post_name"),
                                    "acf": p.get("acf_data"), "content": p.get("post_content")}, ensure_ascii=False) + "\n")
                k += 1
        if k:
            summary["types"][t] = k
        else:
            os.remove(os.path.join(out, "content", f"{t}.jsonl"))
    summary.update(calls=cl.calls, finished=time.strftime("%Y-%m-%dT%H:%M:%S"))
    json.dump(summary, open(os.path.join(out, "summary.json"), "w"), indent=1)
    print(json.dumps({k: summary[k] for k in ("slug", "files", "documents", "types", "calls")}, ensure_ascii=False))


if __name__ == "__main__":
    main()
