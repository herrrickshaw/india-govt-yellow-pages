# Ministry plan — closing the contact gap, ministry by ministry

_Built 2026-10-31 from `data/agents/ministry_coverage.csv` (documents indexed, order-type PDFs read, signers found, roster and email coverage, instruments and contacts mapped). Priority = curated incentive instruments owned × 20 + instruments found × 2 + unread order documents/50 + 15 if no who's-who roster + 5 if no signer email._

## What every ministry needs, in order of payoff

1. **A who's-who roster** (officer → designation → division → phone/email). Without it, signers stay unmatched and divisions stay unknown. Most incentive ministries have none in the repo today (Power, MoHUA, DPIIT, DoT, DoHFW, MoLE, MeitY, Steel, Mines, Coal, MoPNG…). Sources: the ministry site's who's-who / officers / telephone directory page or PDF, the attached-office directories, the scheme portals' 'contact us' pages.
2. **Every order / notification / guideline / gazette PDF read for its signature block.** The expanded fetch (24,577 candidates) is doing this; ministries whose sites are JS-shells or blocked (MoRTH, DoAFW, AYUSH, MoTA, MoFPI, Cooperation, MoEFCC) need their document sections located by hand.
3. **Scheme / incentive pages mapped to a nodal officer or helpdesk** (PLI cells, scheme portals, 'nodal officer' notices) so an instrument has a published door as well as a signer.
4. **Career events attached** (who moved) — already automatic once a person is in the directory.

## Agent groups (run in parallel, one folder each under `data/agents/<group>/`)

### Group A — Energy & infrastructure

| Ministry | docs indexed | order-type | read | signers | with email | roster | instruments | curated | platform | gap to close |
|---|---|---|---|---|---|---|---|---|---|---|
| Power | 1840 | 621 | 827 | 37 | 6 | 0 | 24 | 6 | digifootprint-postpage | no who's-who roster |
| New and Renewable Energy (MNRE) | 1581 | 671 | 638 | 67 | 16 | 127 | 58 | 3 | digifootprint-postpage | maintain |
| Housing and Urban Affairs (MoHUA) | 4145 | 1040 | 1126 | 39 | 2 | 0 | 25 | 5 | digifootprint-postpage | no who's-who roster |
| Road Transport and Highways (MoRTH) | 915 | 148 | 123 | 21 | 1 | 0 | 4 | 3 | js-shell | no who's-who roster; site is js-shell: documents section not crawled |
| Railways (MoR) | 381 | 1 | 1 | 0 | 0 | 0 | 0 | 5 | html | no who's-who roster; no signer emails; curated incentives with no signing contact |
| Ports, Shipping and Waterways (MoPSW) | 1198 | 166 | 162 | 19 | 4 | 147 | 5 | 1 | html | curated incentives with no signing contact |

### Group B — Industry & trade

| Ministry | docs indexed | order-type | read | signers | with email | roster | instruments | curated | platform | gap to close |
|---|---|---|---|---|---|---|---|---|---|---|
| Department for Promotion of Industry and Internal Trade (DPIIT) | 15923 | 2420 | 2027 | 51 | 5 | 0 | 32 | 2 | digifootprint-postpage | no who's-who roster; 393 order docs unread |
| Commerce and Industry (MoCI) | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 2 | digifootprint-postpage | no who's-who roster; no signer emails; curated incentives with no signing contact |
| Micro, Small & Medium Enterprises (MSME) | 260 | 69 | 64 | 17 | 1 | 0 | 0 | 1 | digifootprint-postpage | no who's-who roster; curated incentives with no signing contact |
| Textiles (MoT) | 681 | 200 | 208 | 35 | 4 | 0 | 7 | 2 | digifootprint-postpage | no who's-who roster |
| Heavy Industries (MoHI) | 964 | 56 | 40 | 4 | 1 | 0 | 2 | 0 | blocked | no who's-who roster; site is blocked: documents section not crawled |
| Department of Public Enterprises (DPE) | 2666 | 416 | 255 | 45 | 3 | 0 | 13 | 0 | digifootprint-postpage | no who's-who roster |

### Group C — Digital & science

| Ministry | docs indexed | order-type | read | signers | with email | roster | instruments | curated | platform | gap to close |
|---|---|---|---|---|---|---|---|---|---|---|
| Department of Telecommunications (DoT) | 10964 | 5311 | 1644 | 22 | 11 | 0 | 30 | 0 | digifootprint-postpage | no who's-who roster; 3667 order docs unread |
| Electronics and Information Technology (MeitY) | 614 | 165 | 145 | 26 | 6 | 0 | 6 | 2 | digifootprint-postpage | no who's-who roster |
| Department of Science and Technology (DST) | 2015 | 242 | 248 | 36 | 10 | 0 | 6 | 0 | digifootprint-postpage | no who's-who roster |
| Department of Scientific and Industrial Research (DSIR) | 1253 | 116 | 159 | 17 | 0 | 0 | 2 | 3 | digifootprint-postpage | no who's-who roster; no signer emails |
| Department of Space | 2209 | 3 | 250 | 0 | 0 | 0 | 0 | 1 | html | no who's-who roster; no signer emails; curated incentives with no signing contact |
| Earth Sciences (MoES) | 2497 | 96 | 250 | 28 | 0 | 0 | 5 | 1 | digifootprint-postpage | no who's-who roster; no signer emails |

### Group D — Resources & materials

| Ministry | docs indexed | order-type | read | signers | with email | roster | instruments | curated | platform | gap to close |
|---|---|---|---|---|---|---|---|---|---|---|
| Steel (MoS) | 1711 | 121 | 123 | 20 | 2 | 0 | 1 | 1 | html | no who's-who roster |
| Mines (MoM) | 1020 | 229 | 242 | 21 | 3 | 0 | 1 | 0 | js-shell | no who's-who roster; site is js-shell: documents section not crawled |
| Coal | 2568 | 10 | 4 | 3 | 2 | 67 | 0 | 1 | html | curated incentives with no signing contact |
| Petroleum and Natural Gas (MoPNG) | 1377 | 1 | 1 | 0 | 0 | 0 | 0 | 1 | html | no who's-who roster; no signer emails; curated incentives with no signing contact |
| Department of Chemicals and Petro-Chemicals (DoCP) | 712 | 6 | 4 | 1 | 0 | 100 | 0 | 0 | html | no signer emails |
| Department of Fertilizers (DoFz) | 446 | 3 | 4 | 0 | 0 | 0 | 0 | 1 | html | no who's-who roster; no signer emails; curated incentives with no signing contact |
| Department of Pharmaceuticals (DoPs) | 535 | 90 | 90 | 16 | 5 | 0 | 1 | 2 | html | no who's-who roster |

### Group E — Food, farm, health & people

| Ministry | docs indexed | order-type | read | signers | with email | roster | instruments | curated | platform | gap to close |
|---|---|---|---|---|---|---|---|---|---|---|
| Department of Agriculture and Farmers Welfare (DoAFW) | 117 | 2 | 0 | 0 | 0 | 0 | 0 | 4 | js-shell | no who's-who roster; site is js-shell: documents section not crawled; no signer emails; curated incentives with no signing contact |
| Department of Food and Public Distribution (DFPD) | 352 | 0 | 0 | 0 | 0 | 0 | 0 | 4 | html | no who's-who roster; no signer emails; curated incentives with no signing contact |
| Department of Fisheries (DoF) | 1092 | 481 | 336 | 43 | 3 | 0 | 16 | 2 | digifootprint-postpage | no who's-who roster |
| Food Processing Industries (MoFPI) | 2463 | 3 | 1 | 0 | 0 | 106 | 0 | 3 | blocked | site is blocked: documents section not crawled; no signer emails; curated incentives with no signing contact |
| Cooperation | 362 | 29 | 1 | 0 | 0 | 0 | 2 | 4 | dead | no who's-who roster; site is dead: documents section not crawled; no signer emails; curated incentives with no signing contact |
| Department of Health and Family Welfare (DoHFW) | 9335 | 1853 | 1284 | 40 | 1 | 0 | 41 | 0 | digifootprint-postpage | no who's-who roster; 569 order docs unread |
| AYUSH (MoA) | 58 | 3 | 3 | 0 | 0 | 0 | 0 | 3 | js-shell | no who's-who roster; site is js-shell: documents section not crawled; no signer emails; curated incentives with no signing contact |
| Labour and Employment (MoLE) | 3393 | 703 | 695 | 41 | 1 | 0 | 4 | 4 | digifootprint-postpage | no who's-who roster; curated incentives with no signing contact |
| Skill Development and Entrepreneurship (MSDE) | 62 | 21 | 20 | 5 | 0 | 0 | 4 | 0 | digifootprint-postpage | no who's-who roster; no signer emails |
| Tourism | 1709 | 256 | 302 | 25 | 2 | 0 | 11 | 2 | digifootprint-postpage | no who's-who roster |
| Development of North Eastern Region (MDONER) | 1042 | 221 | 96 | 19 | 4 | 0 | 13 | 2 | digifootprint-postpage | no who's-who roster |

## Per-agent task (identical brief, different ministries)

For each ministry: (1) find the officer directory (who's-who / officers / telephone directory / organisation chart, HTML or PDF, including attached offices and scheme portals) and parse it into `officials.csv` (ministry, website, division, name, designation, room, phones, email, source_url); (2) list the scheme / incentive / policy pages and the notification / order / gazette listing pages, especially on sub-sites the index missed, into `sources.csv` (ministry, kind, url, note); (3) record any scheme nodal officer / helpdesk published on those pages as officials with division = scheme name; (4) write `REPORT.md` with what was found, what was blocked, and what the next crawl should add. Read-only, ~1 request/second, robots respected, stop at any captcha / WAF / login.

## Merge (after the agents)

`officials.csv` rows merge into `data/ministry_officials.csv` (keep the larger roster per ministry); `sources.csv` URLs become new crawl seeds for `ministry_documents/tools/` and candidates for `scripts/signatory_matrix.py`; then re-run `select → fetch → extract → directory → match → matrix`, `policy_contact_linker.py`, `career_tracker.py attach`.
