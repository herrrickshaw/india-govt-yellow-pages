# DDD + LangGraph Implementation Guide

This guide walks through the Domain-Driven Design (DDD) and LangGraph architecture implementation for the India Government Yellow Pages.

## Directory Structure

```
src/
├── __init__.py                    # Main package exports
├── main.py                        # Entry point: initialize & run workflows
├── domain/                        # Domain layer (business logic)
│   ├── __init__.py
│   ├── aggregates.py              # Entity roots: Organization, Official, Policy, PressRelease
│   ├── repositories.py            # Repository interfaces (ABCs)
│   └── value_objects.py           # Immutable value types
├── infrastructure/                # Infrastructure layer (external systems)
│   ├── __init__.py
│   ├── graphify_client.py         # Graphify knowledge graph client
│   └── repositories_impl.py       # Concrete repository implementations
├── workflows/                     # Workflow layer (orchestration)
│   ├── __init__.py
│   └── refresh_workflow.py        # LangGraph monthly refresh pipeline
└── api/                           # API layer (query interface)
    ├── __init__.py
    └── query_api.py               # REST query API
```

## Layer-by-Layer Breakdown

### 1. Domain Layer (`src/domain/`)

**Purpose**: Encapsulate business logic and rules. No external dependencies.

#### Value Objects (`value_objects.py`)
Immutable, validated types:
- `OrganizationId`: Organization identifier
- `OfficialId`: Official identifier
- `ContactInfo`: Address, phone, email, etc.
- `Designation`: Title + rank (Minister=1, Secretary=2, ..., Director=5)
- `Location`: Branch (ug/sg/apx/jud/leg/int) + State

```python
# Example: Creating a designation
designation = Designation.from_title("Principal Secretary")  # Auto-ranks to 2
```

#### Aggregates (`aggregates.py`)
Entity roots that represent domain concepts:

- **Organization**: A govt ministry, department, or agency
  - Invariants: name not empty, ≥3 chars
  - Methods: `update_contact_info()`, `to_graph_node()`, `to_graph_edge()`

- **Official**: A government employee
  - Invariants: name ≥3 chars, not just a rank marker
  - Methods: `update_contact_info()`, `to_graph_node()`, `to_graph_edge(EMPLOYS)`

- **Policy**: A government incentive instrument (open/closed)
  - Invariants: instrument name ≥3 chars
  - Methods: `update_status()`, `to_graph_node()`, `to_graph_edge(OFFERS)`

- **PressRelease**: A PIB press release (6-year historical snapshot)
  - Invariants: release_id and title not empty
  - Methods: `to_graph_node()`, `to_graph_edge(PUBLISHED)`

Each aggregate has a `to_graph_node()` method that produces the Graphify node representation, and an optional `to_graph_edge()` method for linking edges to other entities.

#### Repositories (`repositories.py`)
Abstract interfaces defining query methods:

- `OrganizationRepository`: `find_by_id()`, `find_by_name()`, `find_by_branch()`, `find_by_state()`, `find_all()`
- `OfficialRepository`: `find_by_email()`, `find_by_name()`, `find_by_organization()`, `find_top_by_rank()`
- `PolicyRepository`: `find_open()`, `find_by_ministry()`, `find_by_status()`
- `PressReleaseRepository`: `find_by_ministry()`, `find_by_6year_trend()`, `find_by_90day_recency()`

### 2. Infrastructure Layer (`src/infrastructure/`)

**Purpose**: Implement repositories, provide external system access.

#### Graphify Client (`graphify_client.py`)
Wrapper around Graphify knowledge graph API:
- `upsert_node(type, id, properties)`: Add/update a node
- `upsert_edge(source, edge_type, target, properties)`: Add/update an edge
- `get_node()`, `get_neighbors()`, `query()`: Read operations
- `get_stats()`, `export_nodes()`, `export_edges()`: Snapshots
- `get_metadata()`, `set_metadata()`: Sync tracking

#### Repository Implementations (`repositories_impl.py`)
Concrete implementations backed by CSV data + Graphify:

- `GraphifyOrganizationRepository`: Loads from `organizations_index.csv` + `org_contacts.csv`
- `GraphifyOfficialRepository`: Loads from `officials.csv` + `ministry_officials.csv`
- `GraphifyPolicyRepository`: Loads from `policy_contacts.csv`
- `GraphifyPressReleaseRepository`: Loads from `pib_ministry_contacts.csv`

Each repository:
1. Loads CSV into in-memory cache on init
2. Builds aggregates with domain invariants enforced
3. Implements query methods by filtering cache
4. On `save()`, upserts to Graphify graph

### 3. Workflow Layer (`src/workflows/`)

**Purpose**: Orchestrate multi-step data pipelines with LangGraph.

#### Refresh Workflow (`refresh_workflow.py`)
State machine-driven monthly refresh pipeline:

```
DISCOVERY → LINKAGE → SYNC → COMPLETE
```

**RefreshState**: Dataclass tracking metrics
- `phase`: Current workflow phase
- `discovered_orgs`, `discovered_officials_t1`, `discovered_officials_t2`: Discovery counts
- `linked_policies`, `linked_pib_releases`: Linkage counts
- `graph_nodes_upserted`, `graph_edges_upserted`: Sync counts
- `sync_errors`: Accumulated error messages

**Node Functions**:
1. `discover_organizations()`: Load organizations and officials from CSV
2. `link_policies()`: Join open instruments to ministry top-3 contacts
3. `link_pib_activity()`: Join 6y press releases to ministry top-3 contacts
4. `sync_to_graphify()`: Upsert all entities to knowledge graph
5. `on_complete()`: Mark as complete and log results

**Execution**:
```python
workflow = RefreshWorkflow(org_repo, official_repo, policy_repo, release_repo, graphify)
final_state = workflow.run()
print(final_state.to_dict())  # {phase: "complete", discovered_orgs: 10647, ...}
```

### 4. API Layer (`src/api/`)

**Purpose**: Query interface for the knowledge graph.

#### Query API (`query_api.py`)
REST-ready interface:

**Officials**:
- `search_officials(name, email, ministry_id, state, designation)`: Multi-criteria search
- `get_official(id)`: Fetch one by ID

**Organizations**:
- `search_organizations(name, branch, state)`: Multi-criteria search
- `get_organization(id)`: Fetch one by ID
- `get_organization_officials(org_id, limit=5)`: Top officials by rank
- `get_organization_policies(org_id)`: All policies offered

**Policies**:
- `search_policies(instrument, ministry_id, status, tier)`: Multi-criteria search
- `get_policy(id)`: Fetch one by ID
- `get_policy_contacts(policy_id, limit=3)`: Top contacts per policy

**Press Releases**:
- `get_ministry_pib_activity(org_id)`: PIB stats, 6y trend, 90d recency

**Graph Traversal**:
- `traverse_graph(start_node_id, depth=2)`: BFS from a node

**Stats**:
- `get_stats()`: Overall counts and timestamps

---

## Integration with Existing Pipeline

The DDD architecture **wraps existing Python scrapers** without modifying them:

```
CSV Data (existing)
    ↓
Repository (loads CSV, builds aggregates)
    ↓
Workflow (orchestrates discover → link → sync phases)
    ↓
Graphify Graph
    ↓
Query API (read-only interface)
    ↓
Dashboard / REST endpoints
```

### Migration Path

**Phase 1 (now)**: DDD architecture runs in parallel with existing CSV→DuckDB pipeline
- Existing: `igod_crawl.py` → CSV → DuckDB → `build_dashboard.py` → HTML
- New: CSV → DDD aggregates → Graphify graph

**Phase 2 (next)**: Dashboard queries Graphify (read-only fallback to CSV)
- `dashboard/index.html` fetches `GET /api/graph/officials?name=...`
- Data validation: check node counts match CSV

**Phase 3 (final)**: CSV tables become archive snapshots only
- Graphify is source of truth
- `refresh.sh` stages: scrapers → CSV → repositories → workflow → graph
- DuckDB/CSV used only for historical backups

---

## Running the Architecture

### Simple Demo

```python
from src.main import initialize_system, run_refresh_workflow

# Initialize all components
system = initialize_system()

# Run refresh workflow (discover → link → sync)
run_refresh_workflow(system)

# Query the graph
api = system['query_api']
officials = api.search_officials(name="Amit")
for o in officials:
    print(f"{o['name']}: {o['designation']} ({o['email']})")
```

### Full CLI Execution

```bash
cd /Users/umashankar/india-govt-yellow-pages
python3 -m src.main
```

Output:
```
🏗️  Initializing India Government Yellow Pages DDD Architecture
✓ Graphify client initialized
✓ Repositories initialized
✓ Refresh workflow initialized
✓ Query API initialized

🔄 Running Refresh Workflow
========================================================
[DISCOVER] Found 10647 orgs, 333 T1, 1807 T2
[LINKAGE] Linked 334 open policies to 1002 official contacts
[LINKAGE] Linked 5421 PIB releases to 540 official contacts
[SYNC] Upserted 12288 nodes, 7847 edges
[COMPLETE] Refresh successful. Stats: {phase: "complete", ...}

🔍 Demonstrating Query API
...
```

### Integration with Existing `refresh.sh`

Update the monthly cron orchestration to include DDD sync:

```bash
#!/bin/bash
# scripts/refresh.sh (updated)

python3 scripts/igod_crawl.py              # Phase A
python3 scripts/igod_org_details.py        # Phase B
python3 scripts/ministry_whoswho.py        # Phase C
python3 scripts/link_policy_contacts.py    # Link phase
/usr/bin/python3 scripts/build_db.py       # DuckDB (existing)
python3 scripts/build_dashboard.py         # HTML (existing)

# NEW: Sync to Graphify graph
python3 -m src.main > logs/ddd_sync-$(date +%Y-%m-%d).log

git add data/ dashboard/ logs/
git commit -m "monthly refresh: $(date +%Y-%m-%d)"
git push
```

---

## Architecture Benefits

1. **Separation of Concerns**
   - Domain: business rules (invariants, validation)
   - Infrastructure: persistence (repositories, external APIs)
   - Workflow: orchestration (multi-step pipelines)
   - API: interface (query contracts)

2. **Testability**
   - Aggregate invariants testable in isolation
   - Repositories mockable for workflow tests
   - Graphify client can be stubbed for unit tests

3. **Incremental Updates**
   - Delta detection in repositories
   - Soft-deletes preserve history
   - Graphify metadata tracks sync timestamps

4. **Scalability**
   - Graphify handles native graph queries (vs. relational joins on CSVs)
   - Repositories cache aggregates in memory
   - Workflow nodes can be parallelized

5. **Auditability**
   - `updated_at` timestamps on all entities
   - Soft-deletes preserve audit trail
   - Workflow state logged to JSON

---

## Next Steps

1. **Extend Query API**: Add Flask/FastAPI REST wrappers
   ```python
   from flask import Flask, jsonify
   app = Flask(__name__)
   
   @app.route('/officials/search', methods=['GET'])
   def search_officials():
       return jsonify(api.search_officials(**request.args))
   ```

2. **Add Incremental Sync**: Detect changes in CSV, skip unchanged rows
   ```python
   def incremental_sync(graphify_client, old_csv, new_csv):
       # Compute diff, upsert only changed nodes
   ```

3. **Integrate LangGraph Agent**: Use Claude to suggest policy contacts
   ```python
   from langgraph.agents import create_react_agent
   
   tools = [api.search_officials, api.search_policies, ...]
   agent = create_react_agent(model, tools)
   ```

4. **Expand Graph Queries**: Implement Graphify DSL parser
   ```python
   # "Find all open policies in Agriculture sector"
   results = graphify.query("""
       MATCH (m:Ministry)-[OFFERS]->(p:Policy {status: "open"})
       WHERE p.tier CONTAINS "Agriculture"
       RETURN p.instrument, m.name
   """)
   ```
