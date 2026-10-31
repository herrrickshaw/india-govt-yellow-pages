# India Government Yellow Pages

<!-- how-to-use-with-ai -->
> **New here?** See [How to use this repo with AI (Claude, Gemini, ChatGPT)](HOW_TO_USE_WITH_AI.md) — clone it, paste it into an AI tool, and ask in plain English.


A structured contact repository of Indian government organizations — union
ministries, state departments, apex bodies, judiciary, legislatures and
Indian missions abroad — built from **igod.gov.in** (Integrated Government
Online Directory, NIC/MeitY), the official one-point index of Indian
government websites.

## What you get

| File | Contents |
|---|---|
| `data/organizations_index.csv` | Every organization listed on igod: branch (ug/sg/apx/jud/leg/int), state, category, name, website URL, igod detail-page id (9,461 rows) |
| `data/org_contacts.csv` | Per-organization contact block: address, phone, fax, email, website (134 rows) |
| `data/officials.csv` | Igod who's-who officer directory: name, designation, division, phones, office address, email (333 rows) |
| `data/ministry_officials.csv` | **Tier-2 deep scrape**: each union ministry's own /whos-who page parsed for full officer roster with room/phones/email. 1,807 officials across 17 ministries (1,466 emails) |
| `data/signatories/` | **Who signed what**: officers from the rosters linked to the orders, notifications, circulars, OMs and gazette notifications they signed (read from the PDFs' signature blocks), and an officer × topic matrix — see [`data/signatories/SIGNATORY_MATRIX.md`](data/signatories/SIGNATORY_MATRIX.md) |
| `data/policy_contacts.csv` | Open incentive instruments (digital-twin-for-ipa flat index) joined to owning ministry's top-5 officials (334 rows) |
| `data/pib_ministry_contacts.csv` | Per-ministry PIB press activity (6y + 90d) joined to top-3 contacts (182 rows) |
| `data/yellowpages.duckdb` | All tables above in one DuckDB file for SQL queries |
| `dashboard/index.html` | Self-contained, offline-capable dashboard with stat tiles, searchable views, and 6y PIB inline bar charts |
| `ministry_documents/` | **Ministry-by-ministry document index** (2026-10-26, re-crawled 2026-10-27): ~136,000 orders, notices, reports, guidelines and other files published on 89 union ministry/department websites, each with a direct file link, plus the platform each site runs on and the extractors. See [ministry_documents/README.md](ministry_documents/README.md) |

## Pipeline

```bash
python3 scripts/igod_crawl.py              # Phase A: index every igod listing
python3 scripts/igod_org_details.py        # Phase B: contacts + igod who's-who
python3 scripts/ministry_whoswho.py        # Phase C: tier-2 deep scrape (HTML/PDF)
python3 scripts/link_policy_contacts.py    # Join policies + PIB activity to contacts
/usr/bin/python3 scripts/signatory_matrix.py all   # Who signed which order/notification -> officer x topic matrix
/usr/bin/python3 scripts/build_db.py       # DuckDB (use /usr/bin/python3)
python3 scripts/build_dashboard.py         # Regenerate dashboard/index.html
```

All stages are wired into `scripts/refresh.sh`, which runs monthly via cron `30 10 1 * *`.

## Tier-2 Who's-Who Deep Scrape

`ministry_whoswho.py` walks the website of every union ministry/department:
- Extracts igod quick-links containing "who"
- Probes common paths (`/whos-who`, `/who-is-who`, `/about-us/whos-who`, etc.)
- Retries `.nic.in` domains as `.gov.in` (many old NIC domains are dead)
- Parses **NIC Drupal views-tables** (standard government site template)
- Extracts **embedded/linked PDF who's-who rosters** (via pdfplumber)
- Parses **Next.js payload tables** (headless-WP hybrid sites)

Coverage: **1,807 officials** with **1,466 emails** across **17 ministries**:
- Department of Revenue (415), Expenditure (161), Ports/Shipping (135), MNRE (128), AHD (119), DoCP (101), DoCA (98), DAE (77), Panchayati Raj (71), Coal (67), DLR (65), Defence (61), + 5 more

Known gap: ~78 ministry sites are Akamai-fronted JS-shell templates that render entirely client-side (MeitY, DoT, DST, SandBox, etc.); a real-browser pass with Playwright can reach the DOM but no tables are in the rendered output — they may require clicking/filtering or be on a separate `/staffdirectory` endpoint.

## Who signed what — officers ↔ orders / notifications

`scripts/signatory_matrix.py` joins the two halves of this repo: the officer rosters and the
[ministry document index](ministry_documents/). For every ministry that has a who's-who roster it takes the
orders, notifications, circulars, office memoranda, guidelines and gazette notifications from
`ministry_documents/data/all_documents.csv.gz`, downloads the PDFs (politely, ~1 request/second per host, into a
gitignored cache), reads the signature block on the last pages (`pdftotext`, with a tesseract OCR fallback for
scans) and matches the signatory to a roster officer by name, ministry, designation and rank.

| Output (`data/signatories/`) | Contents |
|---|---|
| `notification_signatories.csv` | One row per signature found: document (ministry, title, date, URL, subject line, file number) → signatory as printed → matched officer (name, designation, division, email, phone, roster) with `confidence` (`high` / `medium` / `low (name only, other ministry)`) — or `unmatched` when the signer is not in any roster |
| `officer_topic_matrix.csv` | Officer × topic: documents signed per topic bucket, date range, example titles, document URLs |
| `officer_topic_pivot.csv` | The same as a wide pivot (one row per officer, one column per topic) |
| `officer_documents.csv` | One row per matched document with its topic buckets — the long form of the matrix |
| `SIGNATORY_MATRIX.md` | Human-readable report: funnel, per-ministry coverage, the matrix, and *contact person by topic* for each ministry |

"Contact person for a topic" means *signed documents on that topic*; it is an inference from the paper trail,
not a published point of contact. Unmatched signatories are real officers missing from the rosters — a
to-do list for the who's-who scrape.

### Names first: the signatory directory, and where those people are now

`signatory_matrix.py directory` aggregates every signer read from the PDFs — roster or no roster — into
`data/signatories/signatory_directory.csv` (per ministry: name, spelling variants, designations, documents signed,
date range, phone/email printed under the signature, topics, example documents, roster match if any). It is built
across **all** ministries with order-type PDFs (`SIG_ALL_MINISTRIES=1 SIG_PER_MINISTRY_CAP=250`), so it is the widest
list of serving officials in this repo; matching against rosters is a later, separate step.

Because the person who signed a 2023 notification may hold another post today, `scripts/career_tracker.py` collects
appointment / transfer / posting news (Whispers in the Corridors, PSU Watch, Sarkari Mirror — robots-respecting,
~1 request/second, cached) plus the DoPT ER-sheet postings of IAS officers, extracts career events
(`data/career/career_events.csv`; regex on titles, Groq for multi-officer reshuffle articles) and attaches each
signer's latest known posting to the directories (`latest_posting*`, `moved_since_signing`). Summary:
`data/career/CAREER_TRACKER.md`. Two-token common names are graded `low`; treat a move as a lead to verify.

```bash
SIG_ALL_MINISTRIES=1 SIG_PER_MINISTRY_CAP=250 /usr/bin/python3 scripts/signatory_matrix.py all   # centre, every ministry
/usr/bin/python3 scripts/career_tracker.py all --days 540 --max-articles 800
```

### State-wise: `scripts/state_pipeline.py`

The same matrix for states and UTs, in their languages. `targets` takes the state-government departments
(igod branch `sg`, 4,280 sites across 36 states/UTs) from `data/organizations_index.csv`; `whoswho` reuses the
ministry who's-who scraper on them; `crawl` reuses the ministry document crawler; `select` keeps orders / GOs /
notifications / circulars by English *and* regional-language title words; `extract` reads signature blocks in
Latin or the state's script (tesseract OCR in the state language for scans; designation words per language in
`INDIC_DESIG`); `translate` romanises Indic-script signatory names and translates subject lines with Groq
(cached in `data/states/translations.json`, rule-based `indic_transliteration` as fallback); `match`/`matrix`
reuse the centre matcher with the state roster (`data/states/state_officials.csv` + IAS/IPS officers of that cadre).

```bash
/usr/bin/python3 scripts/state_pipeline.py all --states UP,TN,KL --max-sites 20 --max-pages 60 --max-docs 300
```

Outputs: `data/states/<ST>/` (candidates, signatures with `signatory_raw` / `signatory` (Latin) / `subject_raw` /
`subject` (English), `notification_signatories.csv`, `officer_topic_matrix.csv`, `SIGNATORY_MATRIX.md`) and
`data/states/STATE_MATRIX.md` (overview). `data/states/go_portals.csv` lists each state's official GO portal and
whether it answered on 2026-10-31; the search-form portals (UP Shasanadesh, Maharashtra GR, AP/TS GOIR) need
dedicated extractors and are not crawled yet — department sites are.

## The data is live

Open `dashboard/index.html` in a browser (works offline, light/dark aware):
- **6 stat tiles**: organizations indexed, with igod detail pages, officials listed, official emails, states/UTs, open policy instruments
- **Officials** — searchable igod who's-who, filterable by state
- **Ministry Roster** — the tier-2 deep scrape, searchable by ministry
- **Organizations** — full index with branch chips and website links
- **Org Contacts** — per-organization address/phone/email
- **Open Policies** — each open instrument with owning ministry's contacts
- **PIB Activity** — per-ministry 6-year release counts as inline bars, 90-day recency, top contacts

## Refresh

Monthly via cron. The directory changes slowly (portfolio reshuffles, transfers). Officials' postings churn faster than sites update, so treat `ministry_officials.csv` as "as published by the ministries", not ground truth.

## See also

`docs/AI_GOVT_AFFAIRS_ANALYSIS.md` — how this dataset slots into a Quorum-style AI government-affairs stack alongside the existing repos (PIB index, Sansad PQ API, e-gazette, PARIVESH, MoSPI connectors).
