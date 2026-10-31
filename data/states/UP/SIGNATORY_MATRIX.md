# UP — who signed what — officers ↔ orders / notifications matrix

_Built 2026-10-31 by `scripts/signatory_matrix.py`. Scope: ministries with a who's-who roster in `data/ministry_officials.csv` (9 ministries/departments)._

## Funnel

| Stage | Count |
|---|---|
| Candidate order/notification/circular/OM/gazette PDFs in the document index | 200 |
| PDFs fetched | 168 |
| PDFs with machine-readable text | 53 |
| PDFs with a detectable signature block | 53 |
| Signatures matched to a roster officer | 9 documents / 5 officers |
| Signatures not matched (person not in any roster, or moved) | 44 |

## Per ministry

| Ministry | candidates | fetched | signature found | matched docs | officers linked |
|---|---|---|---|---|---|
| Additional Sources of Energy Department, Uttar Pradesh | 38 | 38 | 22 | 6 | 3 |
| Administrative Reforms Department, Uttar Pradesh | 11 | 8 | 1 | 0 | 0 |
| Appointment and Personnel Department, Uttar Pradesh | 2 | 2 | 1 | 0 | 0 |
| Dairy Development Department, Uttar Pradesh | 38 | 35 | 4 | 2 | 1 |
| Department of IT & Electronics, Government of Uttar Pradesh | 5 | 3 | 0 | 0 | 0 |
| Department of Legal Metrology (Weights & Measures), Uttar Pradesh | 9 | 9 | 0 | 0 | 0 |
| Food, Civil Supplies and Consumer Affairs Department, Uttar Pradesh | 28 | 25 | 8 | 0 | 0 |
| Ground Water Department, Uttar Pradesh | 38 | 35 | 9 | 0 | 0 |
| Higher Education Department, Uttar Pradesh | 31 | 13 | 8 | 1 | 1 |

## Officer × topic matrix (documents signed)

Full pivot: `officer_topic_pivot.csv`; long form with example titles and URLs: `officer_topic_matrix.csv`; one row per signed document: `officer_documents.csv`.

| Officer | Designation (roster) | Ministry |  | TOTAL |
|---|---|---|---|

## Contact person by topic

For each ministry and topic, the roster officers who signed the most documents on it (name, roster designation, email).

### ACS to govt. of UP, Women Welfare & Child Development & Nutrition Dept. + DG, State Nutrition Mission, Lucknow

| Topic | Contact officers (docs signed) |
|---|---|
| Other / unclassified |  |

### D.M. & Collector, Ambedkar Nagar

| Topic | Contact officers (docs signed) |
|---|---|
| HR: leave / pay / allowances / service rules |  |
| Other / unclassified |  |

### Private Secretary to Minister of State for Finance (Mr. Pankaj Chaudhary), GOI, New Delhi

| Topic | Contact officers (docs signed) |
|---|---|
| Other / unclassified |  |

### Spl Secy to Govt of UP, APC Branch, Lucknow

| Topic | Contact officers (docs signed) |
|---|---|
| Scheme guidelines / implementation |  |

### Spl. Secretary to Govt. of U.P., Higher Education Deptt. + Registrar, Dr. Ram Manohar Lohiya Vidhi Vishwavidalaya, Lucknow

| Topic | Contact officers (docs signed) |
|---|---|
| Other / unclassified |  |

## Signatories missing from the rosters (roster gaps)

People who sign orders for a ministry but are not on its who's-who page / igod / civil lists — candidates to add to the yellow pages.

| Ministry | Signatory (as printed) | Signed as | Documents | Latest |
|---|---|---|---|---|
| Additional Sources of Energy Department, Uttar Pradesh | Preshak | Joint Secretary / Secretary | 3 |  |
| Additional Sources of Energy Department, Uttar Pradesh | Sarvesh Singh | Joint Secretary | 3 |  |
| Food, Civil Supplies and Consumer Affairs Department, Uttar Pradesh | Amresh Chandra | Under Secretary | 3 |  |
| Additional Sources of Energy Department, Uttar Pradesh | Jay Veer Singh | Joint Secretary | 2 |  |
| Additional Sources of Energy Department, Uttar Pradesh | Sudhir Garg | Principal Secretary | 2 |  |
| Additional Sources of Energy Department, Uttar Pradesh | Sunil Kumar Chauhan | Under Secretary | 2 |  |
| Ground Water Department, Uttar Pradesh | Adhishasi Abhiyanta | Director | 2 |  |
| Ground Water Department, Uttar Pradesh | Anita Singh | Principal Secretary | 2 |  |
| Ground Water Department, Uttar Pradesh | Anupam | Director | 2 |  |
| Higher Education Department, Uttar Pradesh | Rajiv Kumar | Secretary | 2 |  |

## Caveats

- A signature block is read heuristically from the last two pages of each PDF: a name line (often in parentheses) followed by a designation line. Scanned PDFs and Hindi-only signature blocks are not read (counted above).
- Matching is by name similarity with a bonus for the same ministry and a matching designation; `confidence` is `high` (near-exact name, same ministry), `medium`, or `low (name only, other ministry)`. Rosters are a snapshot (who's-who pages, igod, DoPT civil lists), so an officer who signed in 2022 may have moved since.
- 'Contact person for a topic' means *signed documents on that topic*, not a published point of contact. Topics are keyword buckets over subject line + title + site category; a document can fall in two buckets.
- Rows with `match_status=unmatched` in `notification_signatories.csv` are real signatories who are not in any roster — a useful list of people to add to the yellow pages.