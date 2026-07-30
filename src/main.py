#!/usr/bin/env python3
"""Main entry point: Initialize DDD architecture and run workflows."""
import json
import sys
from pathlib import Path
from datetime import datetime

from infrastructure.graphify_client import GraphifyClient
from infrastructure.repositories_impl import (
    GraphifyOrganizationRepository,
    GraphifyOfficialRepository,
    GraphifyPolicyRepository,
    GraphifyPressReleaseRepository,
)
from workflows.refresh_workflow import create_refresh_workflow
from api.query_api import QueryAPI


def initialize_system(data_dir: Path = None) -> dict:
    """Initialize the DDD architecture with all components."""
    if data_dir is None:
        data_dir = Path(__file__).resolve().parent.parent / "data"

    print("🏗️  Initializing India Government Yellow Pages DDD Architecture")
    print(f"📁 Data directory: {data_dir}")

    # 1. Initialize Graphify client
    graphify = GraphifyClient()
    print("✓ Graphify client initialized")

    # 2. Initialize repositories
    org_repo = GraphifyOrganizationRepository(graphify, data_dir)
    official_repo = GraphifyOfficialRepository(graphify, data_dir)
    policy_repo = GraphifyPolicyRepository(graphify, data_dir)
    release_repo = GraphifyPressReleaseRepository(graphify, data_dir)
    print("✓ Repositories initialized")

    # 3. Initialize workflow
    refresh_workflow = create_refresh_workflow(
        org_repo, official_repo, policy_repo, release_repo, graphify
    )
    print("✓ Refresh workflow initialized")

    # 4. Initialize query API
    query_api = QueryAPI(
        org_repo, official_repo, policy_repo, release_repo, graphify
    )
    print("✓ Query API initialized")

    return {
        'graphify': graphify,
        'org_repo': org_repo,
        'official_repo': official_repo,
        'policy_repo': policy_repo,
        'release_repo': release_repo,
        'refresh_workflow': refresh_workflow,
        'query_api': query_api,
    }


def run_refresh_workflow(system: dict) -> None:
    """Execute the monthly refresh workflow."""
    print("\n🔄 Running Refresh Workflow")
    print("=" * 60)

    workflow = system['refresh_workflow']
    state = workflow.run()

    print("\n✅ Refresh Complete")
    print("=" * 60)
    print(json.dumps(state.to_dict(), indent=2))

    # Save state to file
    state_file = Path(__file__).resolve().parent.parent / "reports" / "workflow_state.json"
    state_file.parent.mkdir(parents=True, exist_ok=True)
    with state_file.open('w') as f:
        json.dump(state.to_dict(), f, indent=2)
    print(f"📄 Workflow state saved to {state_file}")


def demo_queries(system: dict) -> None:
    """Demonstrate query API usage."""
    print("\n🔍 Demonstrating Query API")
    print("=" * 60)

    api = system['query_api']

    # Demo 1: Get stats
    stats = api.get_stats()
    print(f"\n📊 System Stats:")
    print(f"  - Organizations: {stats['organizations']}")
    print(f"  - Officials: {stats['officials']}")
    print(f"  - Policies: {stats['policies']}")
    print(f"  - Press Releases: {stats['press_releases']}")

    # Demo 2: Search officials
    print(f"\n🔎 Searching officials by name 'Amit':")
    results = api.search_officials(name="Amit")
    for official in results[:3]:
        print(f"  - {official['name']}: {official['designation']} ({official['email']})")

    # Demo 3: Get open policies
    print(f"\n📋 Open policies:")
    policies = api.search_policies(status="open")
    for policy in policies[:3]:
        print(f"  - {policy['instrument']} (Ministry: {policy['ministry_id']})")

    # Demo 4: Get organization
    print(f"\n🏛️  Sample organizations:")
    orgs = api.search_organizations()[:3]
    for org in orgs:
        print(f"  - {org['name']} ({org['state']})")
        officials = api.get_organization_officials(org['id'], limit=2)
        for off in officials:
            print(f"      └─ {off['name']} ({off['designation']})")

    # Demo 5: PIB activity
    print(f"\n📰 Ministry PIB Activity:")
    if orgs:
        pib_stats = api.get_ministry_pib_activity(orgs[0]['id'])
        print(f"  - Ministry: {pib_stats['ministry_id']}")
        print(f"  - Total releases: {pib_stats['total_releases']}")
        print(f"  - Releases in last 90 days: {pib_stats['releases_90d']}")


def export_graph_snapshot(system: dict) -> None:
    """Export Graphify nodes and edges to JSON snapshot."""
    print("\n💾 Exporting Graph Snapshot")
    print("=" * 60)

    graphify = system['graphify']

    snapshot = {
        'timestamp': datetime.utcnow().isoformat(),
        'nodes': graphify.export_nodes(),
        'edges': graphify.export_edges(),
        'stats': graphify.get_stats(),
    }

    snapshot_file = Path(__file__).resolve().parent.parent / "reports" / "graph_snapshot.json"
    snapshot_file.parent.mkdir(parents=True, exist_ok=True)
    with snapshot_file.open('w') as f:
        json.dump(snapshot, f, indent=2, default=str)

    print(f"📁 Graph snapshot saved: {snapshot_file}")
    print(f"   - Nodes: {len(snapshot['nodes'])}")
    print(f"   - Edges: {len(snapshot['edges'])}")


def main():
    """Main entry point."""
    try:
        # Initialize system
        system = initialize_system()

        # Run refresh workflow
        run_refresh_workflow(system)

        # Demo queries
        demo_queries(system)

        # Export graph snapshot
        export_graph_snapshot(system)

        print("\n✨ All operations completed successfully!")
        return 0

    except Exception as e:
        print(f"\n❌ Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
