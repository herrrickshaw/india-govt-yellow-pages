# Group B — officer directories & policy sources (collected 2026-10-31)

Files: `officials.csv` (1028 rows, 975 with email), `sources.csv` (175 rows). All GETs, ~1 req/s/host, browser UA, robots.txt checked (dpiit/msme/texmin/dpe: `Allow: /`; dgft, commerce, dcmsme: no robots.txt; heavyindustries.gov.in/robots.txt returns 403 — site itself served normally). Roughly 25–45 requests per ministry, well under the 150 cap. Nothing was bypassed; no `-k`/`verify=False` was needed anywhere.

## Key finding: four of the six sites share one Next.js CMS with an open WP REST API
`www.dpiit.gov.in`, `www.msme.gov.in`, `www.texmin.gov.in`, `www.dpe.gov.in` (and an *empty* `www.moci.gov.in`) are the same DigiFootprint build. Public pages are client-rendered shells (every path returns 200 + identical 8.6 KB HTML, so HTML crawling yields nothing), but `<site>/cms/wp-json/wp/v2/` is open:
- `directory_post` = officer directory (fields: name, title, phone_number, intercom_number, email_id, secondary_email_id, address; taxonomies `designation_tag`, `departments_tag`).
- `employees` = "Our Team" grouping (acf.teams → directory_post ids) — used as division where `departments_tag` is empty (DPE).
- `schemes_and_services` (+`schemes_services_category`), `documents` (+`documents_category`: Acts and Policy / Gazette Notifications / Orders and Notices / Guidelines…), `central_documents` (+`cd_category`; DPIIT has 15,917 rows), `whats_new`, `pages` (contact-us acf holds WIM/CIO/RTI/grievance officers).
- `media/<id>` is **not** readable (returns null) so the "Our Team" PDF attachments could not be resolved.
- Public route pattern (from the template sitemap, which still points at meity.gov.in): `/ministry/directory`, `/ministry/our-team`, `/offerings/<slug>`, `/documents/orders-and-notices`, `/documents/gazettes-notifications`, `/documents/act-and-policies`, `/whats-new`.

## Per ministry

### DPIIT — 311 officials (287 with email)
- Directory: 307 officers from `directory_post` (258 carry a division tag; designations from `designation_tag`). Contact-us page: WIM/CIO (Dr. Kajal), RTI & grievance (Shri Dalip Kumar Chawla), website (Shri Rajesh Kumar Sinha) — 4 rows.
- Schemes: 13 in CMS (PLI White Goods, IDS 2017, UNNATI 2024, NEIDS, NICDP, SIP, SPRIHA, BHAVYA, J&K scheme, IL, GST budgetary support …). No scheme-level nodal officers published in the scheme records.
- Documents: 514 `documents` (Orders and Notices 168, Acts and Policy 155, Gazette Notifications 115, Publications 76, Report 98) + 15,917 `central_documents`.
- Portals probed: Startup India (AEM, 600 KB pages; contact page = toll-free 1800 115 565 + form, no names), IP India (helpdesk numbers only, 3 office-address tables). Not probed: nsws.gov.in, pli.dpiit.gov.in (PLI White Goods), ipindia who-is-who (menu item exists).
- **Crawl next:** `https://www.dpiit.gov.in/cms/wp-json/wp/v2/central_documents?per_page=100&page=N` (15.9k docs, paginate by `cd_category`), and `https://ipindia.gov.in/organisation-structure` / IP India "Who is who" menu.

### Commerce and Industry (MoCI) — 225 officials (214 with email), all from DGFT
- `www.commerce.gov.in` is a Vite JS shell (9 KB; `/about-us/whos-who` → 404; `sitemap.xml` 404). Its content API needs credentials shipped in `/assets/index-*.js` — **not used**, per instructions. A web search found no standalone DoC telephone-directory PDF; the DoC Annual Report PDFs (`/files/2025-08/Commerce_AR-2024-25-English-1.pdf`) carry office addresses in Annexure A but no officer list. `www.moci.gov.in` CMS exists but has 0 directory rows.
- DGFT (`www.dgft.gov.in/CP/?opt=…`) landing/whos-who/contact-us/regional-authorities are the same 119 KB SPA shell, **but** `?opt=dgft-hq-details` (75 HQ officers, with section + work allocation, room, building, intercom) and `?opt=dgft-ra-details` (150 RA officer rows across all Regional Authorities) are server-rendered tables. `?opt=list-its-officers` lists ITS officer PDFs (as on 01.01.2026 … 2020) — not downloaded.
- Notifications / Public Notices / Trade Notices / Circulars / RoDTEP / FTP pages listed in sources.csv; their listings are populated client-side (`cdn-prod-dgft…/script/content.js`), so a crawler needs a headless browser or DGFT's search API.
- **Crawl next:** the ITS officer PDF behind `?opt=list-its-officers` (as on 01.01.2026), and DoC's `/contactus/` once a JS-capable crawler is available. commerce.gov.in should be marked `js-shell/credentialed-api` in fingerprint.

### MSME — 171 officials (171 with email)
- Ministry directory: 77 officers (all with division tags, e.g. "Under Secretary – Internal Finance Wing"). Contact-us: WIM/CISO Dr. Simmi Chaudhary, Dy CISO Shri Amit Saxena; grievance → champions.gov.in / champions@gov.in.
- Attached office O/o DC-MSME (`dcmsme.gov.in/Contact_HQ.aspx`, ASP.NET, server-rendered): 92 officers with work allocation (division = their allocated schemes/divisions: TCEC, PMV, TCSP, MSE-CDP, ZED …). `/whos-who`-style paths all 302 to an error page; `contacts/help-desk.html` is a 1 KB stub.
- Schemes: 21 in CMS (CHAMPIONS Portal, ODR Portal, PM Vishwakarma, Udyam, National SC-ST Hub, MSE-SPICE/RAMP, TCEC, MSE-CDP, PMEGP …). Portals: champions.gov.in (redirects to .aspx grievance app), samadhaan.msme.gov.in, zed.msme.gov.in (contact = query form, no names), dashboard.msme.gov.in. MCGS/CLCSS have no dedicated page in the CMS.
- **Crawl next:** `https://dcmsme.gov.in/Contact_of_Field_Offices.aspx` (33 MSME-DFOs + 28 branch offices) and `https://www.msme.gov.in/cms/wp-json/wp/v2/our_organisation` (25 attached/autonomous bodies with links).

### Textiles (MoT) — 140 officials (137 with email)
- Ministry directory: 79 officers (66 with division tags; `our_division` empty). Contact-us: WIM/CISO Shri Akhilesh Kumar, RTI Shri Sandeep Kumar, PG Shri Rajeev Ranjan Kumar.
- Attached: O/o Textile Commissioner Mumbai (`txcindia.gov.in/html/contactus.htm`, card layout) 31 HQ officers; DC Handlooms who's-who PDF 21 officers (3 pages, pdfplumber) + WIM; NTTM `nttm.texmin.gov.in/PI/WhosWho` 4 mission officers. `handicrafts.nic.in` timed out; `jutecomm.gov.in` serves a 2.5 KB landing only; `pmmitra.texmin.gov.in` does not resolve (PM MITRA lives at `/offerings/pm-mitra`).
- Schemes: 15 in CMS (PLI, PM MITRA, NTTM, SAMARTH, TUFS, Silk Samagra-2, IWDP, TCDS, IPDS, Kapas Kranti, TEX-RAMPS …). PLI Textiles portal `pli.texmin.gov.in` (IFCI PMA; `/Scheme-Notifications`, helpdesk plitextiles@ifciltd.com, no named officers).
- **Crawl next:** `https://www.txcindia.gov.in/html/contactus.htm` regional-office cards (only HQ parsed) and `https://nttm.texmin.gov.in/PI/Circulars`.

### Heavy Industries (MoHI) — 123 officials (108 with email)
- Drupal site, English at `/en/…` (root 301s to `/hi`; fingerprint "blocked" is wrong — `/en/whos-who` is a 282 KB server-rendered page). 113 officers across 6 tables (Minister, MoS, Officers' Information, NIC, General Services) with location, email, phone, fax, PABX, room. `/en/contact-us` gives IT Manager / WIM mailboxes without names. `/en/nodal-officer-0` links a nodal-officer PDF (not parsed).
- PM E-DRIVE portal `pmedrive.heavyindustries.gov.in/who` (8 scheme officers) and `/contact-us` (4 named scheme contacts). PLI Auto portal `pliauto.in` (IFCI) — one PMA contact. Scheme pages (PLI Auto, PLI ACC, EMPS 2024, PM e-Bus Sewa PSM, FAME II, Capital Goods) each list ~20 PDFs; `/en/notifications`, `/en/notifications-0`, `/en/scheme-notification`, `/en/scheme-guidelines` are the notification listings. Scheme pages expose only generic mailboxes (jspcm-mhi@gov.in).
- **Crawl next:** `https://heavyindustries.gov.in/sites/default/files/Havi_Udyog Bharati_Pathakert1_2025_1-10-25.pdf` (nodal officers) and `https://pmedrive.heavyindustries.gov.in/policy_document` (gazette/notification PDFs).

### DPE — 58 officials (58 with email)
- Directory: 56 officers; no `departments_tag`, so division = "Our Team" group (Office of Minister, Secretary's Office, IF Wing, Policy/Survey divisions …). Contact-us: WIM/CIO Sh. Lucas L Kamsuan (+ NIC cell, e-office helpdesk, web admin mailboxes, kept in sources).
- Only 1 scheme (RDCR). Documents: 82 `documents` (Guidelines 43, Report 20, Personnel Policies 13, PE Survey Report 11, Financial Policies 8) + 2,667 `central_documents`; `pages_detailed_data` has Organization Chart, Work Allocation, Citizen Charter.
- **Crawl next:** `https://www.dpe.gov.in/cms/wp-json/wp/v2/central_documents?per_page=100` (2,667 DPE guidelines/OMs — the real "orders" corpus) and `https://www.dpe.gov.in/cms/wp-json/wp/v2/pages_detailed_data` (work allocation).

## Blocked / empty / caveats
- commerce.gov.in: JS shell + credentialed API — not scraped (0 DoC officers). DGFT SPA listings need JS.
- moci.gov.in CMS: empty. CMS `media/<id>`: unreadable (Our Team PDFs unresolved).
- handicrafts.nic.in: timeout. pmmitra.texmin.gov.in: NXDOMAIN. heavyindustries.gov.in/robots.txt: 403 (treated as no robots file; site content served normally).
- Rows kept as printed: designations may be blank for ~15 persons (e.g. CMS rows with no designation tag); DGFT RA officers legitimately repeat across RAs they hold concurrently. Service/room rows (reception, library, photocopying) were dropped.

## Row counts
| ministry | officials | sources |
|---|---|---|
| Department for Promotion of Industry and Internal Trade (DPIIT) | 311 | 35 |
| Commerce and Industry (MoCI) | 225 | 17 |
| Micro, Small & Medium Enterprises (MSME) | 171 | 44 |
| Textiles (MoT) | 140 | 43 |
| Heavy Industries (MoHI) | 123 | 22 |
| Department of Public Enterprises (DPE) | 58 | 14 |
| **total** | **1028** | **175** |
