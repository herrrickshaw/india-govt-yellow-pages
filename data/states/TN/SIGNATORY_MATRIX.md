# TN — who signed what — officers ↔ orders / notifications matrix

_Built 2026-10-31 by `scripts/signatory_matrix.py`. Scope: ministries with a who's-who roster in `data/ministry_officials.csv` (16 ministries/departments)._

## Funnel

| Stage | Count |
|---|---|
| Candidate order/notification/circular/OM/gazette PDFs in the document index | 252 |
| PDFs fetched | 239 |
| PDFs with machine-readable text | 80 |
| PDFs with a detectable signature block | 81 |
| Signatures matched to a roster officer | 31 documents / 13 officers |
| Signatures not matched (person not in any roster, or moved) | 54 |

## Per ministry

| Ministry | candidates | fetched | signature found | matched docs | officers linked |
|---|---|---|---|---|---|
| Agricultural Engineering Department, Tamil Nadu | 2 | 2 | 0 | 0 | 0 |
| Agriculture and Farmers Welfare Department, Tamil Nadu | 23 | 23 | 6 | 1 | 1 |
| Art and Culture Department, Tamil Nadu | 23 | 22 | 11 | 0 | 0 |
| Backward Classes Most Backward Classes and Minorities Welfare Department, Tamil Nadu | 12 | 12 | 5 | 1 | 1 |
| Civil Supplies and Consumer Protection Department, Tamil Nadu | 15 | 14 | 4 | 3 | 3 |
| Department of Textiles, Tamil Nadu | 2 | 2 | 1 | 0 | 0 |
| Employment and Training Department, Tamil Nadu | 23 | 22 | 8 | 1 | 1 |
| Environment and Climate Change Department, Tamil Nadu | 23 | 22 | 10 | 10 | 1 |
| Fisheries Department, Tamil Nadu | 15 | 13 | 5 | 3 | 2 |
| Food Safety and Drug Administration Department, Tamil Nadu | 15 | 13 | 3 | 0 | 0 |
| Handlooms Department, Tamil Nadu | 6 | 4 | 0 | 0 | 0 |
| Health and Family Welfare Department, Tamil Nadu | 23 | 23 | 10 | 0 | 0 |
| Highways Department, Tamil Nadu | 1 | 1 | 1 | 0 | 0 |
| Horticulture and Plantation Crops Department, Tamil Nadu | 23 | 20 | 9 | 4 | 2 |
| Information Technology Department, Tamil Nadu | 23 | 23 | 0 | 0 | 0 |
| Labour Department, Tamil Nadu | 23 | 23 | 8 | 8 | 4 |

## Officer × topic matrix (documents signed)

Full pivot: `officer_topic_pivot.csv`; long form with example titles and URLs: `officer_topic_matrix.csv`; one row per signed document: `officer_documents.csv`.

| Officer | Designation (roster) | Ministry |  | TOTAL |
|---|---|---|---|

## Contact person by topic

For each ministry and topic, the roster officers who signed the most documents on it (name, roster designation, email).

### Additional Chief Secretary to Government, Environment, Climate Change and Forests Department, Chennai

| Topic | Contact officers (docs signed) |
|---|---|
| Budget / sanction / release of funds / grants |  |
| Committees / meetings / minutes / constitution of |  |
| Licensing / approvals / standards / enlistment |  |
| Other / unclassified |  |
| Scheme guidelines / implementation |  |

### Additional Chief Secretary to Government, Micro Small and Medium Enterprises Department, Secretariat, Chennai

| Topic | Contact officers (docs signed) |
|---|---|
| Committees / meetings / minutes / constitution of |  |

### Additional Chief Secretary to Government, Rural Development and Panchayat Raj Department, Chennai

| Topic | Contact officers (docs signed) |
|---|---|
| Acts / commencement / legislation |  |
| Other / unclassified |  |

### Additional Chief Secretary to Government, Special Initiatives Department, Chennai

| Topic | Contact officers (docs signed) |
|---|---|
| Acts / commencement / legislation |  |
| Statutory rules / gazette notifications (G.S.R. / S.O.) |  |

### Chairman and MD, TNEB, TNPDCL, TNGECL, TANTRANSCO & TNPGCL, Chennai

| Topic | Contact officers (docs signed) |
|---|---|
| Other / unclassified |  |

### Chairman, Inland Waterways Authority of India M/o Ports, Shipping & Waterways, New Delhi

| Topic | Contact officers (docs signed) |
|---|---|
| Legal metrology / consumer protection rules |  |
| Scheme guidelines / implementation |  |

### Commissioner (GOI) Navodaya Vidyalaya Samiti (NVS) D/o School Education & Literacy New Delhi

| Topic | Contact officers (docs signed) |
|---|---|
| Other / unclassified |  |

### Principal Secretary / Chairman and MD, TANSIDCO, Chennai

| Topic | Contact officers (docs signed) |
|---|---|
| Statutory rules / gazette notifications (G.S.R. / S.O.) |  |

### Principal Secretary to Government, Secretariat, Human Resources Management Department, Chennai

| Topic | Contact officers (docs signed) |
|---|---|
| Other / unclassified |  |

### Principal Secretary to Governor, Governor Secretariat, Chennai

| Topic | Contact officers (docs signed) |
|---|---|
| Committees / meetings / minutes / constitution of |  |
| Other / unclassified |  |
| Statutory rules / gazette notifications (G.S.R. / S.O.) |  |

### Secretary to Government BC, MBC & MW Department Secretariat Chennai

| Topic | Contact officers (docs signed) |
|---|---|
| Scheme guidelines / implementation |  |

### Secretary to Government Higher Education Department Secretariat Chennai

| Topic | Contact officers (docs signed) |
|---|---|
| Other / unclassified |  |

### Secretary to Government Labour Welfare and Skill Development Department Secretariat Chennai

| Topic | Contact officers (docs signed) |
|---|---|
| Acts / commencement / legislation |  |
| Legal metrology / consumer protection rules |  |
| Statutory rules / gazette notifications (G.S.R. / S.O.) |  |

## Signatories missing from the rosters (roster gaps)

People who sign orders for a ministry but are not on its who's-who page / igod / civil lists — candidates to add to the yellow pages.

| Ministry | Signatory (as printed) | Signed as | Documents | Latest |
|---|---|---|---|---|
| Art and Culture Department, Tamil Nadu | Apoorva Varma | Additional Chief Secretary | 10 |  |
| Agriculture and Farmers Welfare Department, Tamil Nadu | Samayamurthi | Commissioner | 5 |  |
| Health and Family Welfare Department, Tamil Nadu | Thanjavur IMA | Director of Medical & Rural Health Services, Chennai. / Director of Medical & Rural Health Services,Chennai. | 3 |  |
| Horticulture and Plantation Crops Department, Tamil Nadu | V. Datchinamurthi | Commissioner | 3 |  |
| Backward Classes Most Backward Classes and Minorities Welfare Department, Tamil Nadu | K.G Verma | Deputy Secretary to the Government of India / Director | 2 |  |
| Civil Supplies and Consumer Protection Department, Tamil Nadu | ANUPAM MISHRA | Jt. Secy | 2 |  |
| Food Safety and Drug Administration Department, Tamil Nadu | SUDHIR KUMAR | Jt. Secy | 2 |  |

## Caveats

- A signature block is read heuristically from the last two pages of each PDF: a name line (often in parentheses) followed by a designation line. Scanned PDFs and Hindi-only signature blocks are not read (counted above).
- Matching is by name similarity with a bonus for the same ministry and a matching designation; `confidence` is `high` (near-exact name, same ministry), `medium`, or `low (name only, other ministry)`. Rosters are a snapshot (who's-who pages, igod, DoPT civil lists), so an officer who signed in 2022 may have moved since.
- 'Contact person for a topic' means *signed documents on that topic*, not a published point of contact. Topics are keyword buckets over subject line + title + site category; a document can fall in two buckets.
- Rows with `match_status=unmatched` in `notification_signatories.csv` are real signatories who are not in any roster — a useful list of people to add to the yellow pages.