# Ministry documents — every union ministry/department website, indexed

A ministry-by-ministry index of the documents (orders, notices, reports, guidelines, gazette notifications,
statistics, minutes, press releases…) published on the websites of India's union ministries and departments,
with a direct link to each file. Built 2026-10-26 from the igod.gov.in directory in this repo
(`data/organizations_index.csv`: 53 ministries, 50 departments, 2 independent departments).

## What is here

| File | Contents |
|---|---|
| `data/all_documents.csv.gz` | One row per document (~102,000): ministry, site, source (`api` or `crawl`), title, document group, category, date, file URL, size, language, page it was found on. `zcat` / `pd.read_csv(..., compression="gzip")` |
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

## Gaps (2026-10-26)

- **Unreachable or blocked:** Corporate Affairs (`mca.gov.in`, 403), Consumer Affairs (`doca.gov.in` serves a
  bare lighttpd placeholder), Cooperation, Finance (`finmin.gov.in`), DRDO and Military Affairs (timeouts).
- **Thin results:** DBT, MHA, Youth Affairs, `yas.gov.in`, Personnel (`persmin.gov.in`) — links not
  reachable by either crawler.
- **Umbrella ministries on the shared CMS** (Education, Law, Defence, Health, Commerce) hold little themselves;
  their documents sit on the department sites, which are indexed separately.
- Commerce (`commerce.gov.in`) content API only answers with credentials shipped in its JavaScript — not used.
- DPIIT: 10,414 of the 15,886 file records the API reports; 55 of its 159 bulk pages returned HTTP 500 on
  every retry (2026-10-26) and are skipped, so re-running later may fill them in.
- Crawled sites are capped at 300 pages, so very large sites (MoEFCC, Culture, DAE…) are indexed partially;
  API sites are complete apart from pages that returned server errors (logged in each `summary.json`).
- Dates for crawled links come from the upload path (`/2026/09/`) when present, otherwise blank.

## Re-running

```bash
python3 tools/fingerprint.py           # classify every site (writes data/fingerprint.csv)
python3 tools/run_postpage_all.py      # shared-CMS sites
python3 tools/run_html_all.py          # server-rendered sites
python3 tools/extract_tribal.py        # Tribal Affairs
python3 tools/build_index.py           # merge into all_documents.csv / coverage.csv / DuckDB
```

Run it outside a Dropbox/iCloud-synced folder: in a synced `~/Downloads`, output files that stay open for
minutes were replaced by empty copies mid-write.
