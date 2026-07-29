# AI for Government Affairs — Quorum's playbook mapped to this ecosystem

Source: Quorum, "11 Ways to Use AI for Government Affairs"
(https://www.quorum.us/blog/ways-to-use-ai-for-government-affairs/), analysed
against the knowledge graph of the 42 local repos (graphify global graph,
~26.9k nodes / 45.6k edges).

## 1. Quorum's 11 use cases, and the data asset each one needs

| # | Quorum use case | Underlying data asset | India equivalent source | Already in the repos? |
|---|---|---|---|---|
| 1 | Surface relevant legislation | Bill database | eGazette, PRS, Lok/Rajya Sabha bill lists | Partial — egazette direct-PDF pattern (`WriteReadData/<yr>/<gid>.pdf`) in digital-twin-for-ipa |
| 2 | Analyze legislation (summarize bills) | Bill full text | eGazette PDFs + Unlimited-OCR fallback | Yes — OCR fallback wired across doc-parsing repos |
| 3 | Compare bills across states | State-wise policy corpus | State gazettes, state PCB/industry policies | Partial — `STATE_POLICY_COMPARISON.md`, `POLICY_COMPARISON_WORKBOOK.md` (india-trade-sector-policy-recommendations) |
| 4 | Assess amendment implications | Amendment tracking | Gazette amendment chains (e.g. FCO 3rd Amdt 2025 work) | Pattern proven in digital-twin-for-ipa L33 |
| 5 | **Find key officials & staffers** | **Contact directory** | **igod.gov.in who's-who → THIS REPO** | **Now yes — organizations_index / org_contacts / officials** |
| 6 | Identify policy champions/opponents | Statements + sponsorships | Sansad PQ API (who asks what), PIB releases by ministry | Yes — `sansad.in/api_ls/question/qetFilteredQuestionsAns` + `pib_index.py` (SQL index by date×ministry) |
| 7 | Generate talking points | LLM over positions corpus | Same corpora | Straightforward layer on top |
| 8 | Message variations for outreach | Mailer infra | `send_mailer.py` / `build_mailer.py` (Gmail SMTP, token-free) | Yes — reusable as the outreach channel |
| 9 | Strategic guidance on passage | Sponsorship/viability graph | PQ author × ministry × topic graph | Buildable from Sansad PQ index |
| 10 | Track lawmaker statements real-time | Press/statement feed | PIB releases (indexed), ministry wp-json feeds | Yes — pib_index.py + headless-WP `wp-json` access pattern |
| 11 | Analyze committee transcripts | Hearing records | LS/RS committee reports (PDF), Sansad digital library | Gap — RS sources blocked from this machine; LS PDFs fetchable |

The core insight from Quorum's product: **every AI use case sits on a
boring, well-maintained directory/tracking dataset.** The LLM layer is thin;
the moat is the data plumbing. This repo supplies the single dataset the
ecosystem was missing — the *people/contact* layer (use case #5), which is
also the prerequisite for #7–#9 (you can't target outreach without knowing
who holds the pen).

## 2. What the knowledge graph shows we already have

- **`pib_index.py`** (india-trade-sector-policy-recommendations) — SQL index
  of PIB press releases by date × ministry: the "statement tracking" feed.
- **Sansad PQ API access** — undocumented LS Q&A endpoint indexed to PDFs:
  the "who champions what" signal (question authorship ≈ sponsorship signal
  in a parliamentary system, where private bills rarely move).
- **eGazette direct-PDF + OCR** — the "bill/notification full text" layer.
- **PARIVESH open dashboard API** — regulatory-approval pipeline visibility.
- **MoSPI/RBI/data.gov.in connectors** — the evidence base for talking points.
- **Mailer infrastructure** (`send_mailer.py`, n8n workflows, launchd/cron
  scheduling) — the delivery channel, already battle-tested by the
  watchlist mailer.
- **Ministry-site access patterns** — `wp-json` on headless-WP ministry
  sites, PIB POST traps, etc. (memory: reference_india_ministry_site_access).

## 3. Proposed agent pipeline (LangGraph-style) over these assets

A stateful graph, one node per capability, contact directory as shared state:

```
                        ┌────────────────┐
                        │  watch_gazette │  (eGazette poller + OCR)
                        └──────┬─────────┘
┌────────────────┐             ▼
│  watch_pib     │──────►┌───────────────┐     ┌──────────────────┐
└────────────────┘       │  classifier    │────►│ impact_assessor  │
┌────────────────┐       │ (which sector/ │     │ (LLM: summarize, │
│  watch_sansad  │──────►│  which repo    │     │  diff amendments)│
└────────────────┘       │  cares?)       │     └────────┬─────────┘
                         └───────┬────────┘              ▼
                                 ▼                ┌──────────────────┐
                        ┌────────────────┐        │ stakeholder_map  │
                        │ champion_finder│───────►│ (JOIN officials  │
                        │ (PQ authorship)│        │  .csv on ministry│
                        └────────────────┘        │  + designation)  │
                                                  └────────┬─────────┘
                                                           ▼
                                                  ┌──────────────────┐
                                                  │ brief_composer → │
                                                  │ send_mailer.py   │
                                                  └──────────────────┘
```

- **State**: DuckDB (`yellowpages.duckdb` + pib index + PQ index) — matches
  the repo convention of "tracked tabular data goes in DuckDB".
- **Checkpointing**: LangGraph's sqlite checkpointer, or just the existing
  cron + CSV-state idiom already used by the watchlist mailer.
- **Human-in-the-loop**: outreach drafts stop at a draft/review node —
  consistent with the standing rule that nothing external sends without
  validation (cf. feedback_validate_scan_before_mailer).

## 4. Honest caveats

- igod's officer directory lags real postings (transfers show up late);
  it's a NIC-published snapshot, not an HRMS feed.
- Quorum's #10/#11 (real-time statements, committee transcripts) are the
  weakest India equivalents: no official streaming feed, Rajya Sabha
  sources are network-blocked from this machine, and Sansad TV transcripts
  don't exist as text.
- Emails on ministry sites are often role-based (`secy.moc@nic.in`) rather
  than personal — fine for official correspondence, poor for CRM-style
  tracking.
