# India Government Yellow Pages

A structured contact repository of Indian government organizations — union
ministries, state departments, apex bodies, judiciary, legislatures and
Indian missions abroad — built from **igod.gov.in** (Integrated Government
Online Directory, NIC/MeitY), the official one-point index of Indian
government websites.

## What you get

| File | Contents |
|---|---|
| `data/organizations_index.csv` | Every organization listed on igod: branch (ug/sg/apx/jud/leg/int), state, category, name, website URL, igod detail-page id |
| `data/org_contacts.csv` | Per-organization contact block: address, phone, fax, email, website |
| `data/officials.csv` | Who's-who officer directory: name, designation, division, phones, office address, email (de-obfuscated from `[at]`/`[dot]`) |
| `data/yellowpages.duckdb` | The three tables above in one DuckDB file |

## Pipeline

```bash
python3 scripts/igod_crawl.py        # Phase A: index every listing page (~430 pages, lazy-load aware)
python3 scripts/igod_org_details.py  # Phase B: contacts + who's-who for each org detail page
python3 scripts/build_db.py          # load CSVs into DuckDB
```

Notes on the source's quirks (hard-won):
- Listing pages lazy-load beyond the first ~25 rows via
  `<listing>/organizations_list_more/<start>/<limit>` — the server only
  accepts `limit <= 5` (or the exact final-chunk remainder).
- The endpoint requires a Laravel session cookie (`igod-session`) from a
  prior page load; bare curl gets a meta-refresh redirect to the homepage.
- Officer directories paginate via `/organization/<id>/list_contacts/<start>/10`.
- Emails are obfuscated as `secy[dot]moc[at]nic[dot]in` — de-obfuscated at parse time.
- Many entries (especially autonomous bodies/PSUs) link only to an external
  website with no igod detail page; they appear in the index with a blank
  `igod_org_id`.

## Refresh

The directory changes slowly (portfolio reshuffles, transfers). A monthly
re-run is plenty. Officials' postings churn faster than the site updates, so
treat `officials.csv` as "as published by NIC", not ground truth.

## See also

`docs/AI_GOVT_AFFAIRS_ANALYSIS.md` — how this dataset slots into a
Quorum-style AI government-affairs stack alongside the existing repos
(PIB index, Sansad PQ API, e-gazette, PARIVESH, MoSPI connectors).
