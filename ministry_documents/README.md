# Ministry documents — every union ministry/department website, indexed

A ministry-by-ministry index of the documents (orders, notices, reports, guidelines, gazette notifications,
statistics, minutes, press releases…) published on the websites of India's union ministries and departments,
with a direct link to each file. Built 2026-10-26 from the igod.gov.in directory in this repo
(`data/organizations_index.csv`: 53 ministries, 50 departments, 2 independent departments).

## What is here

| File | Contents |
|---|---|
| `data/all_documents.csv.gz` | One row per document (~136,000): ministry, site, source (`api` or `crawl`), title, document group, category, date, file URL, size, language, page it was found on. `zcat` / `pd.read_csv(..., compression="gzip")` |
| `data/coverage.csv` | One row per site: platform, documents found, how many have a direct URL, pages crawled, errors |
| `data/fingerprint.csv` | Every ministry/department site and the publishing platform it runs on |
| `data/targets.csv` | The 105 union ministries and departments taken from `../data/organizations_index.csv` |
| `tools/` | The extractors (below) |

Not committed (regenerate with the tools; ~105 MB): the per-site raw output `data/sites/<site>/`
(`files.csv`, `documents.jsonl`, `content/*.jsonl` for API sites; `doc_links.csv`, `pages.csv` for crawled
sites) and `data/ministry_documents.duckdb`.

## How each kind of site is read

| Platform | Sites | Method |
|---|---|---|
| Shared ministry CMS (Next.js front end, WordPress back end at `<site>/cms/wp-json`) | ~41 | `extract_postpage.py`: bulk file registry `post-page/central_documents?limit=100&page=N` (direct PDF URL, size, date, language), category tree `taxonomy/documents_category`, listings `document/documents?document_category=<slug>`, plus schemes, divisions, tenders, directory and other content types via `post-page/<type>`. Endpoints found by capturing the sites' own network calls. |
| Server-rendered HTML (Drupal, NIC CMS, custom) | ~39 | `crawl_html.py`: same-site crawl, robots.txt respected, depth 3, ≤300 pages, every document link with its anchor text. Uses `curl` because several servers only speak old TLS versions. |
| JavaScript-only, no shared API | 5 + retries | `crawl_js.py`: renders pages in the Obscura headless browser (standard build) and collects document links. |
| Ministry of Tribal Affairs | 1 | `extract_tribal.py`: the site's own JSON API `/api/v1/documents?pageSize=100`. |

All requests are anonymous, read-only GETs at about one per second per host. No API keys, embedded
credentials or login-protected routes are used, and bot challenges are not bypassed: a site that serves one
is recorded as blocked. Some sites ship a fixed API key or Basic-auth header in their public JavaScript; the
extractors deliberately do not use them.

## Gaps (2026-10-26, re-crawled 2026-10-27)

Re-crawled 2026-10-27 (`tools/recrawl.py`, which keeps every earlier link in `doc_links.prev.csv`): the 14 sites
that hit the 300-page cap were crawled again with a 1,500-page cap (MoEFCC 4,045 → 8,912 links, MHA 1,170 → 3,233,
ISRO 93 → 2,209, Culture, DAE, DEA, DoE, DoR, MEA, MoFPI, Panchayati Raj, Shipping, Steel and DEPwD all up; only ISRO
reached the new cap). Cooperation now answers over curl (incomplete certificate chain, crawled with `--insecure`;
362 links, capped at 300 pages) and Consumer Affairs publishes on `consumeraffairs.gov.in` (713 links). WCD, MoPNG and
NITI were re-crawled; their failing pages (63, 10, 1) failed again and look like permanent server errors.
Finance, DRDO and DBT (`dbtindia.gov.in`) still time out.


Retried 2026-10-26 evening (every failure re-attempted; results below are after the retry):

- **Still unreachable:** Finance (`finmin.gov.in`) and DRDO time out on https/http and www/bare
  variants (Cooperation recovered 2026-10-27). Corporate Affairs (`mca.gov.in`) returns an "Access Denied" bot block and was not pursued.
  Consumer Affairs (`doca.gov.in`) serves only a lighttpd placeholder; its documents are on `consumeraffairs.gov.in` (crawled 2026-10-27).
- **Recovered on retry:** MoSPI (643 documents via its own JSON API, `extract_mospi.py`; was 14), MHA (1,170 via
  the `www.` host; was 16), Rural Development (161 documents / 303 files via `/wp/v2/documents`,
  `extract_wpv2_documents.py`), Military Affairs (answers on `http://www.`; 4 links), Civil Aviation (+79),
  missing file ids resolved for Labour (171), Textiles (41) and four smaller sites; DPIIT complete: its 55
  failing 100-record bulk pages all succeeded as 10-record pages (+5,495 records, 0 unrecoverable), +14 ids resolved.
- **Still thin:** DBT (new Laravel/Inertia site exposes only a landing page and admin routes), Youth Affairs,
  `yas.gov.in`, Personnel (`persmin.gov.in`) — no reachable document links by API, HTML crawl or render.
- **Umbrella ministries on the shared CMS** (Education, Law, Defence, Health, Commerce, Jal Shakti) hold little
  themselves; their documents sit on the department sites, which are indexed separately.
- **Persistent page failures after one retry pass:** WCD (63 pages), MoPNG (10), NITI (1) — listed per site in
  `data/sites/<site>/failed.csv` (not committed; regenerate). MoEFCC's and Fertilizers' earlier "errors" were
  permanent responses (broken links), not transient.
- Commerce (`commerce.gov.in`) content API only answers with credentials shipped in its JavaScript — not used.
- Crawled sites are capped at 300 pages, so very large sites (MoEFCC, Culture, DAE…) are indexed partially;
  API sites are complete apart from pages that returned server errors (logged in each `summary.json`).
- Dates for crawled links come from the upload path (`/2026/09/`) when present, otherwise blank.

## Re-running

```bash
python3 tools/fingerprint.py           # classify every site (writes data/fingerprint.csv)
python3 tools/run_postpage_all.py      # shared-CMS sites
python3 tools/run_html_all.py          # server-rendered sites
python3 tools/extract_tribal.py        # Tribal Affairs
python3 tools/extract_mospi.py         # MoSPI (POST JSON API)
python3 tools/extract_wpv2_documents.py https://www.rural.gov.in/cms/wp-json rural   # no-taxonomy CMS sites
python3 tools/retry_bulk_pages.py dpiit          # re-request 500ing bulk pages in 10- and 1-record chunks
python3 tools/resolve_missing_files.py <site>...  # resolve file ids missing from a bulk registry
python3 tools/recrawl.py moef=https://moef.gov.in:1500 ...  # re-crawl, keeping earlier links
python3 tools/build_index.py           # merge into all_documents.csv / coverage.csv / DuckDB
```

Run it outside a Dropbox/iCloud-synced folder: in a synced `~/Downloads`, output files that stay open for
minutes were replaced by empty copies mid-write.
