# Group A — officer directories and policy sources (collected 2026-10-31)

Files in this folder:

- `officials.csv` — 3,063 officer rows, columns `ministry,website,division,name,designation,room,phones,email,source_url`. Emails de-obfuscated (`[at]`/`[dot]`/`[dash]` → `@`/`.`/`-`); designations kept as printed; `room` holds room / intercom / address as published; `phones` joins office / intercom / fax / mobile with ` ; `.
- `sources.csv` — 246 crawl targets, columns `ministry,kind,url,note` (`kind` ∈ whos-who | schemes | notifications | orders | gazette | portal | helpdesk).

Method: read-only GETs with a desktop Chrome User-Agent, ~1 request/second per host, robots.txt honoured (`Allow: /` on the three digifootprint sites; shipmin.gov.in has the stock Drupal robots; morth and indianrailways return HTML for robots.txt). No CAPTCHA, WAF challenge or login wall was met on any of the six hosts. System `curl` verified TLS everywhere. Approximate request counts: Power 25, MNRE 30, MoHUA 25, MoRTH 30, Railways 60 (35 of them Railway Board directory pages), MoPSW 15.

| Ministry | officials rows | with email | with phone | with division |
|---|---|---|---|---|
| Power | 337 | 336 | 326 | 324 |
| New and Renewable Energy (MNRE) | 147 | 135 | 129 | 5 |
| Housing and Urban Affairs (MoHUA) | 335 | 335 | 285 | 270 |
| Road Transport and Highways (MoRTH) | 354 | 255 | 325 | 139 |
| Railways (MoR) | 1,729 | 20 | 1,698 | 1,729 |
| Ports, Shipping and Waterways (MoPSW) | 161 | 135 | 153 | 161 |
| **Total** | **3,063** | | | |

## Shared pattern: Power, MNRE, MoHUA (digifootprint Next.js + headless WordPress)

All three run the same NIC "digifootprint" stack. The public site (`/en/whos-who`, `/en/schemes`, …) is a client-rendered Next.js shell — every path returns the same ~8 KB HTML, so HTML crawling yields nothing — and the data lives in WordPress at `<site>/cms/wp-json/wp/v2/` (canonical host `cms-<ministry>.digifootprint.gov.in`; both answer). The `our_team` route does not exist. The officer directory is the custom post type **`directory_post`** (ACF: `title`, `name`, `phone_number`, `email_id`, `secondary_email_id`, `fax`, `intercom_number`, `address`, `designation_tag`) with taxonomies **`designation_tag`** (designation text) and **`departments_tag`** (division). Other useful types: `our_division` (work allocation), `our_organisation` (attached offices/PSUs with URLs), `schemes_and_services`, `central_documents` (+ `cd_category`: acts, orders & notices, tenders, scheme docs…), `documents` (+ `documents_category`: Gazette Notifications, Orders and Notices, Guidelines), `whats_new`. `menu-items` is 401. Pagination `?per_page=100&page=N`.

### Power (powermin.gov.in)
- Found: 390 `directory_post` records → 332 unique officers (190 "All Ministry Officials", 18 attached-office/PSU heads, Minister's office, Head of Office/Section, OL division…), all with email. Plus 5 rows from Contact Us / Grievance / RTI (CIO Shri Aadhar Raj, WIM Shri Manish Mishra, Nodal Appellate Authority (PG), Nodal Officer (PG), RTI Nodal Officer Smt. Reetu Jain from the Nodal Officer PDF).
- Also located: RTI "Directory of its officers and employees" PDF (9 pp, 2025-09), organisation-setup PDF, `cd_category` 378 orders and notices (54), 480 Rules framed under Electricity Act 2003 (75), 379 Act and rules (118), 374 scheme and services docs (164), 7 scheme pages (RDSS portal rdss.powermin.gov.in), 25 attached organisations.
- Blocked/empty: nothing blocked. `pages?search=who` → [] (directory is not a page); `initiatives` type empty.
- Add next: `https://www.powermin.gov.in/cms/wp-json/wp/v2/directory_post?per_page=100&page=1` (+ `designation_tag`, `departments_tag`) and `https://www.powermin.gov.in/cms/wp-json/wp/v2/central_documents?per_page=100&page=1`.

### New and Renewable Energy (mnre.gov.in)
- Found: 147 `directory_post` → 144 officers (132 with email); only 2 carry a `departments_tag`, so `division` is mostly blank (the designation tag carries e.g. "Joint Secretary (Solar)"). Contact Us names JS Anupam Kumar; the `documents` item "Designated Authority and Nodal officer" gives the CVO (Lalit Bohra) and the PIDPI officer (Sunita Dhewal). 24 scheme pages (PM Surya Ghar, PM-KUSUM, rooftop solar, PLI solar PV, Green Hydrogen Mission, bioenergy, GEC, HRD…) with portal links.
- Also located: `cd_category` 394 "Contact Us" holds **seven officer-directory PDFs** — MNRE Telephone Directory (as on 03.09.2025, 5 pp: intercom / room / floor / landline / email, divisions as headings), SECI, IREDA, NIBE, NISE, NIWE and a contractors directory. The MNRE PDF is a wrapped multi-column layout; it was not parsed into rows because the JSON directory covers the same people, but it is the only source with *division headings* and deserves a layout-aware parse. `cd_category` 371 Current Notices (576), 370 Orders and Notices (576), 349 Acts and Policies (129), 367 Guidelines (19), 366 Schemes (10).
- Blocked/empty: nothing blocked; grievance page has no named officer (CPGRAMS link only).
- Add next: `https://mnre.gov.in/cms/wp-json/wp/v2/directory_post?per_page=100` and `https://mnre.gov.in/static/uploads/2025/08/90b7421af007e75e202025b87849ee8a.pdf` (telephone directory, for divisions).

### Housing and Urban Affairs (mohua.gov.in)
- Found: 311 `directory_post` → 309 officers (all with email; 244 with division tags such as Office of Minister, Housing Division, CPHEEO, NIC, DMRC). Contact Us ACF list gives the CISO (JS Praveer Kumar), two LIMBS nodal officers and the IT-cell mailbox. The Grievance Redressal page carries the PG Cell officers (4) and the **table of Public Grievance Officers of 16 MoHUA organisations as on 26.02.2026** (CPWD, L&DO, Directorate of Estates, DDA, NBCC, TCPO, NCRPB, DMRC, PAO, DUAC, BMTPC, CGEWHO, HPL, HUDCO, NBO, NCHF) → 22 rows.
- Also located: `documents_category` 146 Gazette Notifications (48), 140 Orders and Notices (16), 147 Guidelines (22); `cd_category` 718 Acts and Rules (106), 475 Advisories and Circulars to States/UTs (31); 12 scheme pages with portals (PMAY-U MIS/dashboard, SBM-U, AMRUT, Smart Cities, PM SVANidhi, DAY-NULM, NUDM, PM-eBus Sewa, eSampada, Urban Challenge Fund); 17 attached organisations with URLs.
- Blocked/empty: nothing blocked.
- Add next: `https://www.mohua.gov.in/cms/wp-json/wp/v2/directory_post?per_page=100&page=1` and `https://www.mohua.gov.in/cms/wp-json/wp/v2/documents?documents_category=146&per_page=100` (gazette).

## Road Transport and Highways (morth.gov.in)
- Platform: Angular SPA (hash routing, `/#/directory`) over a Laravel backend at **`https://morth.gov.in/backend/api/`**; `morth.nic.in` serves the same shell. Static HTML and the JS bundles contain no API URL; the base was found from the browser network log (`/backend/api/all-menu`).
- Found: **`/backend/api/directory?page=N&per_page=200`** → 352 officers (Minister to section staff, with phone / intercom / room / email; `type` = category id). **`/backend/api/our-team`** → 32 named categories with 104 senior officers, used to name the division for 139 rows; the remaining 215 rows have `type` ids (10, 14–17, 20–54) that no public endpoint names (`whoiswho-category`, `directory-category`, `team-category`, `whos-who-type` → 404), so their `division` is blank. Contact Us gives the WIM (JS Udit Agrawal) and the RTI/Grievance JS (C.N. Singh) → 354 rows. Five records had a phone number typed in the email field; moved to `phones`.
- Also located: `all-menu` lists every slug; `/backend/api/<slug>` returns a page tree with `files[].files_data[]` (PDF paths relative to `https://morth.gov.in/backend/`): `gazettes-notifications` (335 KB), `orders-and-notices` (1.1 MB), `schemes-and-services` (6 MB; wings Highways / Road Transport / Road Safety / Land Acquisition / Others), `acts-and-rules`, `policies-and-regulations`, `guidelines`, `public-notices`, `comprehensive-compendium-circular`, `our-wings`, `our-organisation`.
- Blocked/empty: nothing blocked; grievance page has no named officer.
- Add next: `https://morth.gov.in/backend/api/directory?page=1&per_page=200` (then page=2) and `https://morth.gov.in/backend/api/gazettes-notifications` (same shape for `orders-and-notices`).

## Railways (indianrailways.gov.in + rb.indianrailways.gov.in)
- Platform: server-rendered Java CMS (`/publicView/...`, PDFs via `/admin/cms/downloadCmsDoc?path=...`). The ministry site's `/ministry/directory` holds only **42 entries** (MR / MoSR secretariats; the `orgparentId` filter has no effect; 2 pages at `items=100`). The full directory is on the **Railway Board site**: `https://rb.indianrailways.gov.in/home/Directory?page=N&size=75&type=T&description=` with three types — 1 = Railway Board Directory (23 pages → **1,445** unique officers; division = level + directorate badge, e.g. "Secretary's Branch / SECRETARY'S BRANCHES", "Traffic / Traffic Commercial", "Associate Offices / RRB"), 2 = GMs and DRMs Directory (12 pages → **510** officers of zonal railways / production units), 3 = Disaster Management Directory (15 pages; listed in sources, not parsed). Cards (`div.member-item`) carry designation, name, two badges, phone (Rly Tel + PSTN), fax, room — **no email field is published**, hence only 20 emails (from the ministry directory and the contact page). Contact Us names the WIM (PED C&IS Mandeep Singh Bhatia) and the CPIO (D.K. Biswas).
- Also located: 38 Railway Board directorate pages (`/show-directorate/view/<id>`, each with circulars/orders), `rb…/documents/gazettes-notifications`, ministry `/documents/acts|publications|reports`, `/offerings/schemes-and-services` (orgparentId 1 Passenger Services, 4 Other Services), Rail Madad, IREPS, RRB.
- Blocked/empty: legacy `/railwayboard/view_section.jsp` paths are 404 (old site retired). Grievance page: CPGRAMS / 139 only.
- Add next: `https://rb.indianrailways.gov.in/home/Directory?page=1&size=75&type=1&description=` (iterate pages 1–23; type=2 pages 1–12; ~1.6 MB per page because of inline SVG icons) and `https://rb.indianrailways.gov.in/show-directorate/list`.

## Ports, Shipping and Waterways (shipmin.gov.in)
- Platform: Drupal, server-rendered. **`/en/who-s-who`** is a single page with 33 division tables (Name / Designation / Room No-Intercom / Tel(O) / Tel(Res)-Mobile / eMail / Residence) → **148 officers** (Minister's office to CR in-charge; Ports, Shipping, IWT, Sagarmala/IPRCL/ALHW, PHRD, DGLL, Finance, Vigilance, IT, NIC, TRW, Pr. CCA…). `/en/about-us/contactus` lists wing-wise nodal Directors / DS (13 rows) → 161 total.
- Also located: Orders menu (`/en/orders/officeorders`, `circulars`, `policy`, `guideline`, `mou-agreements`, `miscellaneous`, `RTI`), Act & Rules (`/en/act-and-rules/Act|rules|regulations`, India Code link), Sagarmala division page + sagarmala.gov.in, SBFAS/SbDS shipbuilding portals, `/en/organization/listoforganization` (30+ ports / PSUs / attached offices with URLs), dashboard `shipmin.dashboard.nic.in`, citizen charter. The order listings show only 2–5 PDFs on first view and no pager markup — check `?page=N` / the view's exposed filters when crawling.
- Blocked/empty: `/en/about-us/organization-chart` → 400 (correct slug `/en/about-us/organizational-chart`); grievance page has no named officer.
- Add next: `https://shipmin.gov.in/en/who-s-who` and `https://shipmin.gov.in/en/orders/officeorders`.

## Notes for the crawler
- digifootprint sites: use the JSON endpoints only; HTML fetches of `/en/...` are wasted requests.
- MoRTH: API base `/backend/api/`; files under `/backend/documents/uploaded/...` (paths in JSON are relative).
- Row-count summary: Power 337 · MNRE 147 · MoHUA 335 · MoRTH 354 · Railways 1,729 · MoPSW 161 = 3,063.
