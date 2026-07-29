# India Government Yellow Pages

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
| `data/policy_contacts.csv` | Open incentive instruments (digital-twin-for-ipa flat index) joined to owning ministry's top-5 officials (334 rows) |
| `data/pib_ministry_contacts.csv` | Per-ministry PIB press activity (6y + 90d) joined to top-3 contacts (182 rows) |
| `data/yellowpages.duckdb` | All tables above in one DuckDB file for SQL queries |
| `dashboard/index.html` | Self-contained, offline-capable dashboard with stat tiles, searchable views, and 6y PIB inline bar charts |

## Pipeline

```bash
python3 scripts/igod_crawl.py              # Phase A: index every igod listing
python3 scripts/igod_org_details.py        # Phase B: contacts + igod who's-who
python3 scripts/ministry_whoswho.py        # Phase C: tier-2 deep scrape (HTML/PDF)
python3 scripts/link_policy_contacts.py    # Join policies + PIB activity to contacts
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
