# Group D — Resources & materials: officer directories and policy sources

Run date: 2026-10-31. Method: read-only `curl` GETs with a Chrome-like User-Agent, about 1 request/second per host, ~25–40 requests per ministry (well under the 150 cap). Raw pages kept in `raw/`; parser is `parse_officials.py` (re-runnable against `raw/`). Outputs: `officials.csv` (814 rows), `sources.csv` (124 rows).

None of the seven sites use the shared Next.js `/cms/wp-json/wp/v2/` CMS (all 404/500). Robots.txt: steel.gov.in has one (no disallow on the paths used); the others return 404/403/500 for robots.txt.

| Ministry | officials.csv rows | Directory source(s) | sources.csv rows |
|---|---|---|---|
| Steel (MoS) | 120 | /telephone (109) + /public-grievance (11) | 19 |
| Mines (MoM) | 163 | JSON API /admin/whosData | 14 |
| Coal | 81 | /about-us/whos-who (69) + Coal Controller Org (11) + PG cell (1) | 22 |
| Petroleum and Natural Gas (MoPNG) | 155 | /en/page/38 (116) + PNGRB Directory PDF (39) | 24 |
| DoCP | 105 | /who-who (103) + nodal officer + WIM | 14 |
| DoFz | 171 | /en/department/telephone-directory (125) + RTI cell CPIO/FAA (44) + contact-us (2) | 14 |
| DoPs | 19 | /en/whos-who | 17 |
| **Total** | **814** | | **124** |

Rows where the same officer appears under several divisions (MoPNG, Mines, DoF FAAs) are kept as printed — they are multiple charges, not parse errors. Emails are de-obfuscated (`[at]`, `[dot]`, `{dot}`, `[dash]`, `[in]`).

## Steel (MoS) — https://steel.gov.in (Drupal)
- Found: **Telephone Directory** `/telephone` = 17 tables (Name / Division / Room / EPBAX / Office / Email). Designation is only embedded in the name cell ("X, PS to HSM", "PS: Y"); the first row of each table (the principal officer — Minister, MoS, Secretary, AS&FA, each JS/EA/Director) has no designation printed, so 12 rows have a blank designation. Same data is served as "Our Team" at `/organisational-setup-of-ministry-of-steel`. 109 officers.
- `/public-grievance`: Appellate Authority + grievance officers of the Ministry and 10 PSUs (SAIL, RINL, NMDC, MOIL, MECON, KIOCL, MSTC, OMDC, BSLC …) — 11 rows, division = "Public Grievance Officer - <PSU>".
- Schemes/policy pages: PLI specialty steel `/pli`, R&D scheme, NSP 2017, DMI&SP, scrap policy, Vision 2047 draft; orders: `/quality-control-orders`, `/orders` (board appointments); RR notifications, tenders. No PLI nodal officer or helpdesk is published on `/pli`.
- Blocked/empty: `https://research.steel.gov.in/applicant` — **TLS certificate expired** (curl 60), not bypassed. `/contact-us` has only a generic mailbox (itgs-steel@gov.in). `/right-information` has no CPIO table (links only).
- Crawler should add next: `https://steel.gov.in/telephone` (re-parse with first-row designation inferred from table order) and `https://steel.gov.in/quality-control-orders`.

## Mines (MoM) — https://mines.gov.in/webportal/ (Angular SPA, Laravel-style API at /admin/)
- Found: the SPA bundle `main.*.js` defines `Re_serviceURL="https://mines.gov.in/admin/"`; the Who's Who page calls `POST /admin/whosData` with an empty body (GET returns 405). One such empty-body POST — identical to what every page view performs, no parameters, read-only — returned **163 officers** with NAME, DESIGNATION, CONTACTNO, MOBILENO, EMAILID, ADDRESS (room), and `OFFICE_CATEGORY` (used as division: Minister, MoS, Secretary, JS, Mines I–VI, Metal I–IV, NCMM, NMET Secretary, PG cell, IBM camp office, NIC …). `whosAddMoreData` returned status 400/empty.
- Other SPA routes (`our-divisions`, `our-teams`, `gazette-notifications`, `orders-notices`, `circulars`, `schemes-and-sevices`, `nationalmineralpolicy`, `mineralauctionaummary`) pull data via `POST /admin/categoryData` / `childdata` with parameters I did not reverse-engineer, so those listings were **not fetched** (recorded in sources.csv as routes). PDFs live at `https://mines.gov.in/admin/download/<id>.pdf`.
- Critical Minerals Mission officers appear in whosData under `NCMM` (5) and `NMET Secretary` (7).
- Crawler should add next: `POST https://mines.gov.in/admin/whosData` (empty body) and work out the `categoryData` payload for `gazette-notifications` / `orders-notices` (open the SPA in a headless browser once and capture the XHR body).

## Coal — https://coal.nic.in (= coal.gov.in, Drupal)
- Found: `/about-us/whos-who` — 8 level-grouped tables, 69 officers (repo had 67; division now populated from the group heading: Minister's Office, MoS's Office, Secretary's Office, Additional Secretary, JS/Advisors/DDG, Directors/DS, US/AD). `/public-information/public-grievance-cell` names Director (PG). 
- Attached office **Coal Controller Organisation** (`coalcontroller.gov.in`): `/who-s-who` 9 officers, `/contact-us` OSD, `/public-grievances` Director (PG) — 11 rows.
- Scheme / order pages: `/central-sector-schemes`, `/major-statistics/national-coal-gasification-mission` (Rs 8,500 cr gasification financial-incentive scheme PDFs, Sep–Oct 2026), `/acts-rules-policies`, Nominated Authority (`/nominated-authority/*`: auction-allotment, single-window-system, national-coal-index, compensation and termination orders), `/whats-new`, tenders; MSTC auction portal; CMSS/PM GatiShakti portal.
- Empty: `/rti/pio-details-of-ministry-coal` has no HTML table (PIO list is a 2019 PDF); `/about-us/senior-officials-details` and `/agencies-under-ministry` 404 (menu labels only); no dedicated "coal exchange" page found on the site.
- Crawler should add next: `https://coal.nic.in/whats-new` (all scheme notices land here as dated PDFs) and `https://www.coalcontroller.gov.in/who-s-who`.

## Petroleum and Natural Gas (MoPNG) — https://mopng.gov.in (custom PHP; root and most paths return 500, must use `/en/...`)
- Found: Who's Who `/en/page/38` — one table with division header rows (141 rows → 116 officers, division = O/o Minister, GP Division, Refinery, Marketing, E&P, Vigilance, Parliament Cell, IT Cell, etc.). `/en/page/39` Phone Directory is the same table plus section numbers.
- **PNGRB** (`pngrb.gov.in`): no HTML directory; "Contact Us" links a PDF `/pdf/Directory-eng.pdf` (Annexure-I, 68 lines) → 39 officers by division (Monitoring, Authorisation, Technical, Commercial, Consumer Affairs, Legal, IT …).
- Scheme pages: National Policy on Biofuels `/en/page/11` (+ 1G/2G/biodiesel sub-pages), CBG/SATAT `/en/refining/compressed-bio-gas`, EBP, PMUY/Ujjwala 2.0, natural-gas schemes + CGD network, model state CBG policy PDF; orders `/en/page/21`; E&P other notifications; circulars `/en/page/22,29,30`; PNGRB public notices and regulations; OALP, GOBARdhan portals.
- Blocked/empty: `/en/rti/cpios-appellate-authority` → **HTTP 500**; `/en/page/42` (Industry Emergency Contact) is populated client-side per PSU tab (no data in HTML); **SATAT portal** `https://satat.co.in/` — TLS chain fails verification (unable to get local issuer); read once with `-k` as a known-bad public host: it is an Angular shell under `/satat/` with no contact data in the HTML.
- Crawler should add next: `https://mopng.gov.in/en/page/39` (phone directory, superset) and `https://pngrb.gov.in/pdf/Directory-eng.pdf` (re-fetch monthly; PDF changes in place).

## Department of Chemicals and Petro-Chemicals (DoCP) — https://chemicals.gov.in (Drupal)
- Found: `/who-who` — one table with section header rows; 126 rows → 103 officers (repo had 100; division now filled: Minister, MoS, Secretary, JS, Economic Adviser, Directors/DS, US, sections). Plus Nodal Officer (IT Rule 2009) and Web Information Manager → 105.
- Scheme pages: `/schemes`, PCPIR `/pcpir` (status table for Dahej, Vizag–Kakinada, Paradeep + policy PDF), Plastic Park, **BHAVYA Rasayan** (new 2026 scheme + flyer PDF); notifications `/notifications`, QCOs (`/bis-standard`, `/chemicals-bis-standard`, `/petrochemicals-bis-standard`), `/other-notifications`, tenders, RR. Organisation chart PDF dated 15-04-2026.
- Empty: no PCPIR/PLI nodal officer or scheme cell published; `/rti`, `/cpio`, `/telephone-directory` 403/404. No separate PCPIR portal exists on the site.
- Crawler should add next: `https://chemicals.gov.in/who-who` (keep) and `https://chemicals.gov.in/notifications` (QCO/gazette PDFs).

## Department of Fertilizers (DoFz) — https://fert.gov.in (Drupal 11; fert.nic.in does not resolve)
- Found: `/en/department/telephone-directory` — Drupal view, 128 cards (designation / name / division badge; ext / phone / fax / email; room) → 125 officers with division. `/en/connect/rti-cell` — CPIO & First Appellate Authority by subject (30 rows → 44 officer-role rows, division = "RTI CPIO - <subject>" / "RTI First Appellate Authority - <subject>", covering P&K, Urea, DBT, PM-PRANAM, MDA, Movement, FICC …). `/en/connect/contact-us` — WIM and CIO (AS, nodal officer for court cases).
- Scheme pages: `/en/offerings/schemes-services` (PM-PRANAM, MDA), Urea policy, P&K (NBS) policy, fertilizer projects; `/en/documents/notification`, `/en/documents/orders_and_notices`, tenders, reports.
- Empty: `/en/connect/grievance-redressal` is a CPGRAMS pointer only; `/contact-us` without `/en` 404s.
- Crawler should add next: `https://fert.gov.in/en/connect/rti-cell` (subject→officer mapping is the best scheme-cell proxy) and `https://fert.gov.in/en/documents/notification`.

## Department of Pharmaceuticals (DoPs) — https://pharma-dept.gov.in (Drupal; default language Hindi, use `/en/`; pharmaceuticals.gov.in does not resolve)
- Found: `/en/whos-who` — 21-row table (senior officers only, Minister to Directors) → 19 officers with phone, intercom, office address, email.
- Scheme pages: `/en/schemes` (index with PLI Pharma, PLI bulk drugs, Bulk Drug Parks, SPI, SMDI, PRIP notices + gazette PDFs), PLI pharma page, Bulk Drug Parks page, Medical Device Industry (SMDI) page with 2026 calls for proposals, PRIP gazette (01-10-2025) and portal `prip.pharma-dept.gov.in`, DPCO review orders, Jan Aushadhi.
- Blocked/empty: `/en/cpios`, `/en/contactus`, `/en/agencies-under-department` → **HTTP 500**; PRIP portal homepage is a Drupal shell with no contact data; no PLI cell / helpdesk / nodal officer is published on the scheme pages (PLI applications route through the project management agency, not named on-site).
- Crawler should add next: `https://pharma-dept.gov.in/en/schemes` (dated PDFs) and retry `https://pharma-dept.gov.in/en/cpios` when the 500 clears.

## Cross-cutting notes
- No CAPTCHA / WAF / login wall was encountered on any ministry page. Two hosts fail TLS verification (research.steel.gov.in expired; satat.co.in chain) — only satat.co.in was read with `-k`, once, as a public page.
- The only non-GET request was the empty-body `POST /admin/whosData` on mines.gov.in (the SPA's own read call; GET is 405).
- Minister-level rows for the C&F family (Nadda, Dikshit, Sharma …) appear in DoCP, DoFz and DoPs because each department publishes them; de-duplicate on (name, designation) if merging into the ministry-wide roster.
