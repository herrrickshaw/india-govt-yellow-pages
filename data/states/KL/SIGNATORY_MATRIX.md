# KL — who signed what — officers ↔ orders / notifications matrix

_Built 2026-10-31 by `scripts/signatory_matrix.py`. Scope: ministries with a who's-who roster in `data/ministry_officials.csv` (11 ministries/departments)._

## Funnel

| Stage | Count |
|---|---|
| Candidate order/notification/circular/OM/gazette PDFs in the document index | 240 |
| PDFs fetched | 204 |
| PDFs with machine-readable text | 47 |
| PDFs with a detectable signature block | 47 |
| Signatures matched to a roster officer | 3 documents / 2 officers |
| Signatures not matched (person not in any roster, or moved) | 44 |

## Per ministry

| Ministry | candidates | fetched | signature found | matched docs | officers linked |
|---|---|---|---|---|---|
| Agriculture Development and Farmers Welfare Department, Keral | 32 | 32 | 3 | 2 | 1 |
| Animal Husbandry Department, Kerala | 32 | 32 | 1 | 0 | 0 |
| Archives Department, Kerala | 1 | 1 | 1 | 0 | 0 |
| Co-operation Department, Kerala | 32 | 5 | 0 | 0 | 0 |
| Dairy Development Department, Kerala | 32 | 32 | 3 | 1 | 1 |
| Department of Sainik Welfare, Kerala | 32 | 32 | 21 | 0 | 0 |
| Drugs Control Department, Kerala | 10 | 9 | 2 | 0 | 0 |
| Environment & Climate Change Department, Kerala | 32 | 25 | 5 | 0 | 0 |
| Finance Department, Kerala | 4 | 4 | 0 | 0 | 0 |
| Food and Civil Supplies Department, Kerala | 1 | 0 | 0 | 0 | 0 |
| Forest and Wild Life Department, Kerala | 32 | 32 | 11 | 0 | 0 |

## Officer × topic matrix (documents signed)

Full pivot: `officer_topic_pivot.csv`; long form with example titles and URLs: `officer_topic_matrix.csv`; one row per signed document: `officer_documents.csv`.

| Officer | Designation (roster) | Ministry |  | TOTAL |
|---|---|---|---|

## Contact person by topic

For each ministry and topic, the roster officers who signed the most documents on it (name, roster designation, email).

### Additional Chief Secretary, Home & Vigilance Department, Kerala

| Topic | Contact officers (docs signed) |
|---|---|
| Other / unclassified |  |

### Director, Agriculture Development and Farmers Welfare Dept

| Topic | Contact officers (docs signed) |
|---|---|
| Other / unclassified |  |

## Signatories missing from the rosters (roster gaps)

People who sign orders for a ministry but are not on its who's-who page / igod / civil lists — candidates to add to the yellow pages.

| Ministry | Signatory (as printed) | Signed as | Documents | Latest |
|---|---|---|---|---|
| Department of Sainik Welfare, Kerala | Gavarnarutè Utaravin Prakaran | Deputy Secretary / Joint Secretary | 16 |  |
| Department of Sainik Welfare, Kerala | R. Tara Devi | Secretary | 9 |  |
| Department of Sainik Welfare, Kerala | Pakarp | Joint Secretary / Secretary | 6 |  |
| Department of Sainik Welfare, Kerala | Jayashree M | Joint Secretary | 3 |  |
| Department of Sainik Welfare, Kerala | Raju Narayan | Secretary | 3 |  |
| Environment & Climate Change Department, Kerala | SUNEEL PAMIDI | DIRECTOR / Secretary | 3 |  |
| Forest and Wild Life Department, Kerala | SARWESHWAR JHA | Jt. Secy | 3 |  |
| Drugs Control Department, Kerala | MANDEEP K BHANDARI | Jt. Secy | 2 |  |
| Forest and Wild Life Department, Kerala | PRADEEP KUMAR | Principal Secretary. / Secretary | 2 |  |

## Caveats

- A signature block is read heuristically from the last two pages of each PDF: a name line (often in parentheses) followed by a designation line. Scanned PDFs and Hindi-only signature blocks are not read (counted above).
- Matching is by name similarity with a bonus for the same ministry and a matching designation; `confidence` is `high` (near-exact name, same ministry), `medium`, or `low (name only, other ministry)`. Rosters are a snapshot (who's-who pages, igod, DoPT civil lists), so an officer who signed in 2022 may have moved since.
- 'Contact person for a topic' means *signed documents on that topic*, not a published point of contact. Topics are keyword buckets over subject line + title + site category; a document can fall in two buckets.
- Rows with `match_status=unmatched` in `notification_signatories.csv` are real signatories who are not in any roster — a useful list of people to add to the yellow pages.