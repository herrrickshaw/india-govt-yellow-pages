# India Government Yellow Pages — DDD + LangGraph Architecture

## Overview

This document describes a **Domain-Driven Design (DDD)** architecture for the yellow pages system, orchestrated with **LangGraph** for multi-step workflows, and backed by **Graphify** knowledge graphs for storage, querying, and incremental updates.

## Domain Model

### Core Aggregates

#### 1. **Organization Aggregate**
- **Entity**: Organization (Aggregate Root)
- **Value Objects**: 
  - `OrganizationId` (igod org id or auto-generated)
  - `Name` (canonical from detail page <title>)
  - `Location` (branch: ug/sg/apx/jud/leg/int, state)
  - `ContactInfo` (address, phone, fax, email, website)
- **Invariants**:
  - Name is never empty
  - Canonical name is from igod detail page (not listing abbreviation)
  - Website URL is validated
- **Repositories**: `OrganizationRepository`
  - `findById(id)`, `findByName(name)`, `findByBranch(branch)`, `findByState(state)`
  - Backed by Graphify graph queries

#### 2. **Official Aggregate**
- **Entity**: Official (Aggregate Root)
- **Value Objects**:
  - `OfficialId` (auto-generated UUID)
  - `Name` (de-obfuscated email ok, phones as list)
  - `Designation` (ranked: Minister→Secretary→AS→JS→Director)
  - `ContactInfo` (phones, email, office address, room number)
  - `Organization` reference (foreign key to Organization)
- **Invariants**:
  - Name length >= 3, not a rank marker
  - Email format validated (after de-obfuscation)
  - Phones are comma-separated list
- **Repositories**: `OfficialRepository`
  - `findByOrganization(orgId)`, `findByEmail(email)`, `findByName(name)`
  - Supported sources: igod who's-who, ministry who's-who (tier-2)

#### 3. **Policy Aggregate**
- **Entity**: Policy (Aggregate Root)
- **Value Objects**:
  - `PolicyId` (from digital-twin-for-ipa flat index)
  - `Instrument` (policy name)
  - `Status` ("open" / "closed" / "in-force", inferred from status text)
  - `OwningOrganization` reference
  - `Description` (what companies get)
- **Repositories**: `PolicyRepository`
  - `findOpen()`, `findByMinistry(org)`, `findByStatus(status)`

#### 4. **PIBActivityAggregate**
- **Entity**: PressRelease (Aggregate Root)
- **Value Objects**:
  - `ReleaseId` (from pib_index.sqlite)
  - `Ministry` reference
  - `Date`, `Title`, `URL`
  - `Year` (for grouping 6y trends)
- **Repositories**: `PressReleaseRepository`
  - `findByMinistry(orgId)`, `findByDateRange(start, end)`, `findBy6YearTrend()`

---

## Workflow Orchestration with LangGraph

### High-Level Workflows

```
discovery_phase
  ├─ igod_list_crawler (BFS seed pages → 431 listings)
  ├─ igod_detail_extractor (134 detail pages → contacts + who's-who)
  └─ ministry_whoswho_scraper (95 ministry sites → tier-2 deep scrape)

linkage_phase
  ├─ policy_to_official_linker (join open instruments → top contacts)
  └─ pib_to_official_linker (join 6y ministry activity → top contacts)

refresh_phase
  ├─ incremental_delta (since last run: new orgs, updated emails)
  └─ graph_sync (commit delta to Graphify)

query_phase
  ├─ search_officials (full-text by name/email/designation)
  ├─ search_policies (by ministry, status, instrument)
  └─ graph_traverse (all contacts for a policy, all policies for a ministry)
```

### LangGraph Node Definitions

```python
from langgraph.graph import StateGraph
from typing import TypedDict, List

class OrganizationState(TypedDict):
    org_id: str
    name: str
    branch: str
    state: str
    website: str
    officials: List[str]  # official IDs
    policies: List[str]   # policy IDs
    pib_releases: List[str]  # release IDs

class RefreshState(TypedDict):
    phase: str  # "discovery" | "linkage" | "graph_sync"
    discovered_orgs: int
    linked_policies: int
    linked_pib: int
    graph_nodes_upserted: int
    graph_edges_upserted: int
    timestamp: datetime

# Workflow: monthly refresh
refresh_workflow = StateGraph(RefreshState)

def discover_organizations(state: RefreshState) -> RefreshState:
    """BFS seed pages, lazy-load listings, extract contacts."""
    # igod_crawl.py + igod_org_details.py + ministry_whoswho.py
    state["discovered_orgs"] = 10647
    state["phase"] = "linkage"
    return state

def link_policies(state: RefreshState) -> RefreshState:
    """Join open instruments to owning-ministry officials."""
    # policy_contacts.csv generation
    state["linked_policies"] = 334
    state["phase"] = "graph_sync"
    return state

def link_pib_activity(state: RefreshState) -> RefreshState:
    """Join PIB releases (6y) to ministries, rank by recency."""
    # pib_ministry_contacts.csv generation
    state["linked_pib"] = 182
    return state

def sync_to_graphify(state: RefreshState) -> RefreshState:
    """Upsert all nodes/edges into Graphify knowledge graph."""
    # Graphify API: create_node / create_edge for all entities
    state["phase"] = "complete"
    return state

refresh_workflow.add_node("discover", discover_organizations)
refresh_workflow.add_node("link_policies", link_policies)
refresh_workflow.add_node("link_pib", link_pib_activity)
refresh_workflow.add_node("graph_sync", sync_to_graphify)

refresh_workflow.add_edge("discover", "link_policies")
refresh_workflow.add_edge("link_policies", "link_pib")
refresh_workflow.add_edge("link_pib", "graph_sync")
refresh_workflow.set_entry_point("discover")
```

---

## Graphify Knowledge Graph Schema

### Node Types

| Node Type | Fields | Example ID |
|-----------|--------|------------|
| `Organization` | id, name, branch (ug/sg/apx/jud/leg/int), state, category, website, contact_email | `org:moc` |
| `Official` | id, name, designation, email, phones, office_address, source ("igod"\|"ministry") | `official:secy-moc-20260730` |
| `Policy` | id, instrument, ministry_id, tier, status, description, source_url | `policy:coal-aif` |
| `PressRelease` | id, ministry_id, date, title, url, category | `pib:2026-07-30-1` |
| `Ministry` | id, name, 6y_release_count, 90d_count, latest_release_date | `min:coal` |

### Edge Types

| Source | Target | Relation | Metadata |
|--------|--------|----------|----------|
| Organization | Official | `EMPLOYS` | rank (1-5 seniority), source |
| Ministry | Policy | `OFFERS` | status, tier, since_date |
| Ministry | PressRelease | `PUBLISHED` | category, impact_score |
| Policy | Official | `CONTACT_FOR` | top_contact_rank (1-5) |
| Official | PressRelease | `AUTHORED_BY` | implicit (via ministry) |

### Query Examples (Graphify DSL)

```graphql
# Find all open policies offered by Ministry of Coal
MATCH (m:Ministry {name: "Ministry of Coal"})-[OFFERS]->(p:Policy {status: "open"})
RETURN p.instrument, p.tier, p.description

# Find top 3 contacts for a policy
MATCH (p:Policy {instrument: "Agriculture Infrastructure Fund"})-[CONTACT_FOR]-(o:Official)
ORDER BY o.rank ASC
LIMIT 3
RETURN o.name, o.email, o.phones

# Find all ministries with press releases in the last 90 days
MATCH (m:Ministry)-[PUBLISHED]->(r:PressRelease)
WHERE r.date >= now() - 90d
RETURN m.name, count(r) as release_count
ORDER BY release_count DESC

# Find ministries offering policies in Agriculture sector
MATCH (m:Ministry)-[OFFERS]->(p:Policy)
WHERE p.category CONTAINS "Agriculture"
RETURN m.name, collect(p.instrument)

# Incremental delta since last run
MATCH (o:Official {updated_at: {since: "2026-07-30T00:00:00Z"}})
RETURN o.id, o.email, o.organization_id
```

---

## Incremental Update Strategy

### Delta Detection

**At refresh time:**
1. Query Graphify for all `updated_at >= last_run`
2. Scan new CSV data for new/changed rows (checksum on name+email+phones)
3. Diff against prior CSV snapshot

**Changes detected:**
- New official (email/phones changed but name same)
- Email updated (phone or address changed)
- Organization deleted or moved
- Policy status changed

**Action:**
- **New**: insert node, create EMPLOYS edge
- **Updated**: MERGE on id, update properties
- **Deleted**: soft-delete (add `deleted_at` timestamp, don't remove edges)

### Incremental Sync

```python
def incremental_sync(graphify_client, old_officials_csv, new_officials_csv):
    """Compute delta, upsert only changed nodes."""
    old = read_csv(old_officials_csv)
    new = read_csv(new_officials_csv)
    
    # Checkpoint: load from Graphify
    last_sync = graphify_client.get_metadata("official_sync_timestamp")
    
    deltas = compute_diff(old, new)
    
    upserted = 0
    for official in deltas['new'] + deltas['updated']:
        graphify_client.upsert_node(
            'Official',
            official['id'],
            {
                'name': official['name'],
                'email': official['email'],
                'phones': official['phones'],
                'updated_at': now_iso()
            }
        )
        graphify_client.upsert_edge(
            'Official', official['id'],
            'EMPLOYS', 'Organization', official['org_id'],
            {'rank': official['rank']}
        )
        upserted += 1
    
    graphify_client.set_metadata("official_sync_timestamp", now_iso())
    return {'upserted': upserted, 'deleted': len(deltas['deleted'])}
```

---

## Data Flow Diagram

```
┌─────────────┐
│  igod.gov   │
│  NIC Drupal │
└──────┬──────┘
       │ lazy-load, detail pages
       ▼
┌──────────────────┐     ┌──────────────────┐
│  Organizations   │────▶│  Officials (T1)  │
│  10,647 rows     │     │  333 rows        │
└──────┬───────────┘     └──────────────────┘
       │
       │ canonical names, emails
       ▼
┌──────────────────┐
│  Graphify Graph  │
│  Organization    │
│  nodes           │
└────────┬─────────┘
         │
    ┌────┼────┐
    │         │
    ▼         ▼
 Ministry  Official
  Nodes    Nodes (T1)
           (333)
           
┌──────────────────┐
│  Ministry Sites  │
│  HTML/PDF/Next   │
└──────┬───────────┘
       │ tier-2 deep scrape
       ▼
┌──────────────────┐
│  Officials (T2)  │
│  1,807 rows      │
└──────┬───────────┘
       │
       ▼
┌──────────────────────┐
│ Graphify Officials   │
│ Nodes (T2)           │
│ 1,807 nodes, ranked  │
└────────┬─────────────┘
         │
         ├─────────────────────────┐
         │                         │
         ▼                         ▼
    ┌──────────────┐    ┌──────────────────┐
    │  Policies    │    │  PIB Releases    │
    │  334 nodes   │    │  122k nodes      │
    │              │    │  (6y snapshot)   │
    └──────┬───────┘    └──────┬───────────┘
           │                   │
           └────────┬──────────┘
                    ▼
        ┌─────────────────────┐
        │   CONTACT_FOR edge  │
        │   JOIN PUBLISHED    │
        │   (top officials    │
        │    per policy/min)  │
        └────────┬────────────┘
                 ▼
        ┌──────────────────┐
        │  Dashboard/Query │
        │  (read-only)     │
        └──────────────────┘
```

---

## Implementation Roadmap

### Phase 1: Core Repositories (Week 1)
- [ ] `OrganizationRepository` backed by Graphify BFS queries
- [ ] `OfficialRepository` with full-text search
- [ ] Unit tests for aggregate invariants

### Phase 2: LangGraph Workflows (Week 2)
- [ ] `RefreshWorkflow` with 4 nodes (discover → link → sync)
- [ ] Incremental delta detection
- [ ] Error recovery (partial sync, retry nodes)

### Phase 3: Graphify Sync (Week 3)
- [ ] Graphify client with batch upsert
- [ ] Incremental edge creation (EMPLOYS, OFFERS, PUBLISHED)
- [ ] Metadata tracking (sync timestamp, checksums)

### Phase 4: Query API (Week 4)
- [ ] `/officials/search?name=...&email=...&ministry=...`
- [ ] `/policies/open?ministry=...&tier=...`
- [ ] `/ministries/{id}/officials` (with rank ordering)
- [ ] `/graph/traverse?start=policy:xyz` (transitive officials, policies)

---

## Benefits of This Architecture

1. **Separation of Concerns**: Domain logic (invariants, rules) isolated from orchestration (workflows) and storage (Graphify)
2. **Testability**: Aggregate tests mock repositories; workflow tests mock services
3. **Scalability**: Graphify handles graph queries natively (vs. relational joins on CSVs)
4. **Incremental Updates**: Delta detection avoids re-crawling unchanged data
5. **Auditability**: Soft-deletes + `updated_at` timestamps enable historical tracking
6. **Composability**: Workflows can be interrupted, resumed, or chained for ad-hoc tasks

---

## Migration Path from CSV

**Current state:** 6 CSV files → DuckDB tables → dashboard

**Proposed migration:**
1. **Week 1–2**: Keep CSV→DuckDB pipeline running in parallel
2. **Week 2–3**: Implement Graphify sync; validate edge/node counts vs. CSV
3. **Week 3–4**: Switch dashboard to query Graphify (read-only clone CSV as fallback)
4. **Post-migration**: CSV tables become archive snapshots only; Graphify is source of truth

**Validation checkpoints:**
- Node counts match (10.6k orgs, 2.1k officials, 334 policies, 122k PIB)
- Edge counts match (EMPLOYS ~2k, OFFERS ~400, PUBLISHED ~5k)
- Search results identical (officials by name, policies by ministry)
