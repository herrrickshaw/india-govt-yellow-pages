# Group C – officer directories & policy sources (collected 2026-10-31)

Folder: `data/agents/groupC/`. Outputs: `officials.csv` (1689 rows), `sources.csv` (62 rows), scripts `pull_cms.py` (WP-JSON puller), `parse_cms.py`, `parse_extra.py`, `probe.py`; raw JSON/HTML/PDF under `raw/` (fetch log `raw/fetch_log.txt`, 149 requests in total, ~1 req/s per host, browser UA, robots.txt checked – all five CMS sites are `Allow: /`; inspace.gov.in robots lists the allowed `?id=` pages).

## Key finding: one shared CMS
DoT, MeitY, DST, DSIR and MoES all run the same Next.js shell over a WordPress CMS at `<site>/cms/wp-json/wp/v2/`. The officer directory is the custom post type **`directory_post`** (ACF: `name, title, phone_number, email_id, secondary_email_id, fax, intercom_number, address`; designation and division via the `designation_tag` / `departments_tag` taxonomies), and **`employees`** groups officers into divisions (`acf.teams` = directory_post ids). MeitY deviates: designation is the string `acf.designation`, division is `acf.department_tag[].tag`, and `employees.acf.our_employees` holds inline officer records. Schemes are `schemes_and_services`, divisions `our_division`, attached offices `our_organisation`; documents are `documents` + `central_documents` with `documents_category` / `cd_category` taxonomies (Orders and Notices, Gazette Notifications, Circulars …). Public routes: `/ministry/directory`, `/contact-us`, `/rti`, `/offerings/schemes-and-services`, `/documents`. Everything parsed is read-only JSON – no WAF, no captcha on any of the five.

## Per ministry

### Department of Telecommunications (DoT) — 390 rows (344 from CMS directory)
* Found: 344 directory_post officers + 57 division groups (341 mapped to a division), 28 division pages (division mailboxes: LFA, WMO, CVO, IT), 11 schemes (PLI, TTDF, TDIP, 100 5G Labs, SASCI…) with scheme mailboxes; eservices.dot.gov.in publishes a licence-wise officer PDF (9 named ADET/ADG/US officers) and a service→nodal-cell table incl. WPC regional licensing offices; PLI-telecom portal (SIDBI PMA, 3 named managers); DBN (ex-USOF) official mailbox. Documents: 1,564 `documents` (Orders and Notices 1,264; Gazette 62; Unified License 216) + 10,990 `central_documents` (Circulars 889, Gazette 75, Access Service 1,985); eservices circular listing 23 pages.
* Blocked/empty: usof.gov.in and wpc.dot.gov.in time out (DBN and eservices supersede them); dot.gov.in `our-team` page is empty (acf.file ""); DoT `contact_us_details` empty.
* Crawl next: `https://www.dot.gov.in/cms/wp-json/wp/v2/documents?documents_category=<Orders and Notices id>&per_page=100` and `https://eservices.dot.gov.in/circular-notifications-others?page=N` (0–22).

### Electronics and Information Technology (MeitY) — 736 rows (322 from CMS directory, 314 from the officer-list PDF, 91 scheme/division contacts)
* Found: 301 directory_post + 21 inline officers (Secretary/AS/JS offices, Group Heads, CCA); "List of Officers/Staff as on 31.3.2026" PDF (name+designation only – 314 rows not in the directory, no phone/email/division); WIM/CIO/RTI officers on /contact-us; ISM CEO + office (ism.gov.in/our-team); scheme nodal mailboxes for PLI LSEM, PLI IT-HW 1.0/2.0, SPECS, EMC/EMC 2.0, ECMS, M-SIPS, MPMS (incl. IFCI PMA mailboxes). Documents: 340 `documents` + 649 `central_documents` (Gazette 24, Vacancies 112); ISM has its own notices/guidelines/gazette/tender listings.
* Blocked/empty: main pages are JS shells (esdm/pli is 3 KB) – not fought; ecms.meity.gov.in TLS handshake fails from Python (retry with curl); pli.meity.gov.in does not resolve; `departments_tag`/`designation_tag` taxonomies unused on MeitY (fields inline instead). 301 directory_post rows lack email for ~12 and phone for ~30 records.
* Crawl next: `https://ism.gov.in/notifications/gazette-notification` (+ /guidelines, /notices) and `https://www.meity.gov.in/cms/wp-json/wp/v2/central_documents?per_page=100&cd_category=<Gazette id>`.

### Department of Science and Technology (DST) — 369 rows (201 from CMS directory, 143 programme-officer contacts, 22 TDB)
* Found: 201 directory_post + 33 groups (191 mapped); 31 programme pages (INSPIRE, FIST, PURSE, SATHI, SAIF, NQM, NSM, NM-ICPS, SEED, WISE-KIRAN, NGP, CCM…) each listing programme officers (name/designation/phone/email) → extracted; WIM/CIO on /contact-us; TDB directory (8 captioned tables, 22 officers); ANRF e-PMS helpdesk. Documents: 237 `documents` (Orders and Notices 39) + 2,022 `central_documents` (Call For Proposals 413, Scheme and Services 314, Orders and Notices 47).
* Blocked/empty: DST `rti` page content empty; `our-team` points at "Meet the Secretary"/biodata docs, not a directory; anrf.res.in does not resolve (portal is anrfonline.in; its login is captcha-gated – not touched); `departments_tag` missing on 10 officers.
* Crawl next: `https://www.dst.gov.in/cms/wp-json/wp/v2/central_documents?cd_category=<Call For Proposals id>&per_page=100` and `https://tdb.gov.in/tdb-directory`.

### Department of Scientific and Industrial Research (DSIR) — 56 rows (33 from CMS directory, 22 scheme officers)
* Found: 33 directory_post + 7 groups (29 mapped); 10 scheme pages (SIRO, RDI in-house R&D, PRISM, PACE, CRTDH, A2K+, FI, PFRI…) each with a named scheme officer (Scientist F/G) and mailbox (prism-dsir@gov.in etc.) → extracted; CIO/WIM on /contact-us. Documents: 42 `documents` (Gazette 8, Guidelines 9, Acts and Policy 11) + 1,253 `central_documents` (Schemes 70, gazette 15 under misspelt slug 'ghazette', RTI 36, Report 826).
* Blocked/empty: `cd_category` "Directories" (61) is mislabelled – contains PACE call-for-proposal PDFs, no officer directory; grievance page content is "."; `our-team` empty. No separate PRISM/SIRO portals found linked (online application lives on dsir.gov.in).
* Crawl next: `https://www.dsir.gov.in/cms/wp-json/wp/v2/central_documents?cd_category=<Schemes id>&per_page=100` and `https://www.dsir.gov.in/cms/wp-json/wp/v2/documents?per_page=100`.

### Department of Space (ISRO / IN-SPACe) — 51 rows (14 named)
* Found: dos.gov.in redirects to isro.gov.in (static HTML, Cloudflare but no challenge). RTI officer pages per centre: DOS_list.html and ISRO_HQ_list.html parsed (Transparency/Nodal/AA/CPIO/APIO with names, phones, emails); index page lists 19 more centre pages (vssc_list, lpsc_list, sdsc_list, … INSPACe_list). contact.html: ICRB, OMPR, NRSC data centre, NSIL, legal and welfare nodal officers (designations only). IN-SPACe (inspace.gov.in) is a ServiceNow portal – HTML is client-rendered, but `api/now/sp/page?id=inspace_team` returns JSON: 5 leaders with names, 27 team members with title+email only (member-detail API 404s, so names left blank rather than inferred); `?id=inspace_contact_us` gives directorate mailboxes + phone.
* Blocked/empty: no who's-who/telephone directory for DoS/ISRO HQ beyond the RTI lists; no central orders/gazette listing on isro.gov.in; IN-SPACe sitemap.do empty; `?id=contact_us` 404 (correct id is `inspace_contact_us`).
* Crawl next: the 19 remaining `https://www.isro.gov.in/<centre>_list.html` PIO pages and `https://www.inspace.gov.in/api/now/sp/page?id=announcement_for_oppo` (+ `inspace_orgstruct`, `inspace_board`).

### Earth Sciences (MoES) — 87 rows (79 from CMS directory)
* Found: 79 directory_post + 8 groups (61 mapped); /rti page has a CPIO / First Appellate Authority table by division (room, phone, email) → extracted; WIM/CIO/CPIO on /contact-us; 3 umbrella schemes (PRITHVI, DOM, Mission Mausam); 10 attached institutions listed. Documents: 253 `documents` (Press Release 215, Guidelines 11, Orders and Notices 7) + 2,489 `central_documents` (Gazettes Notifications 50, Monthly Reports 85, Archives 1,157).
* Blocked/empty: `our-team` = former secretaries' biodata; division taxonomy nearly unused (1 `our_division`); attached institutes (IMD, INCOIS, IITM, NIOT…) have their own sites – not crawled.
* Crawl next: `https://www.moes.gov.in/cms/wp-json/wp/v2/central_documents?cd_category=<Gazettes Notifications id>&per_page=100` and `https://www.moes.gov.in/cms/wp-json/wp/v2/documents?documents_category=<Orders and Notices id>`.

## Summary of officials.csv
| ministry | rows | named | with email | with phone | with division |
|---|---|---|---|---|---|
| Department of Science and Technology (DST) | 369 | 320 | 367 | 237 | 359 |
| Department of Scientific and Industrial Research (DSIR) | 56 | 41 | 55 | 54 | 52 |
| Department of Space | 51 | 14 | 51 | 13 | 51 |
| Department of Telecommunications (DoT) | 390 | 359 | 389 | 306 | 387 |
| Earth Sciences (MoES) | 87 | 87 | 87 | 84 | 69 |
| Electronics and Information Technology (MeitY) | 736 | 683 | 410 | 305 | 421 |
| **total** | **1689** | | | | |

Rows without a name are published role mailboxes/helpdesks (division = scheme or office, designation says what it is). Emails are de-obfuscated (`[at]`/`[dot]`); designations kept as printed; `room` parsed from the address where present. `source_url` is the exact JSON record, page or PDF the row came from.

## Hosts contacted (requests)
www.inspace.gov.in 42, www.dot.gov.in 18, www.meity.gov.in 16, www.dst.gov.in 15, www.dsir.gov.in 12, www.moes.gov.in 12, www.isro.gov.in 7, pli-telecom.udyamimitra.in 4, ism.gov.in 3, tdb.gov.in 3, dbn.gov.in 3, eservices.dot.gov.in 3, anrfonline.in 1, www.dos.gov.in 1, saralsanchar.gov.in 1, www.anrfonline.in 1

No captcha, login wall or WAF challenge was hit; the only "captcha" seen was the ANRF portal's login box, which was not used. Timeouts: usof.gov.in, wpc.dot.gov.in; DNS failures: anrf.res.in, pli.meity.gov.in; TLS failure (Python only, not retried with curl): ecms.meity.gov.in.
