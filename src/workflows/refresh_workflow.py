"""LangGraph workflow orchestration for monthly refresh."""
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Any
from enum import Enum

try:
    from langgraph.graph import StateGraph
except ImportError:
    # Fallback for manual state graph implementation if langgraph not installed
    StateGraph = None


class RefreshPhase(Enum):
    """Refresh workflow phase enumeration."""
    DISCOVERY = "discovery"
    LINKAGE = "linkage"
    SYNC = "sync"
    COMPLETE = "complete"
    FAILED = "failed"


@dataclass
class RefreshState:
    """State machine for refresh workflow."""
    phase: RefreshPhase
    timestamp: datetime = field(default_factory=datetime.utcnow)

    # Discovery phase metrics
    discovered_orgs: int = 0
    discovered_officials_t1: int = 0
    discovered_officials_t2: int = 0

    # Linkage phase metrics
    linked_policies: int = 0
    linked_pib_releases: int = 0
    policy_contacts_created: int = 0
    pib_contacts_created: int = 0

    # Sync phase metrics
    graph_nodes_upserted: int = 0
    graph_edges_upserted: int = 0
    sync_errors: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert state to dictionary for serialization."""
        return {
            'phase': self.phase.value,
            'timestamp': self.timestamp.isoformat(),
            'discovered_orgs': self.discovered_orgs,
            'discovered_officials_t1': self.discovered_officials_t1,
            'discovered_officials_t2': self.discovered_officials_t2,
            'linked_policies': self.linked_policies,
            'linked_pib_releases': self.linked_pib_releases,
            'policy_contacts_created': self.policy_contacts_created,
            'pib_contacts_created': self.pib_contacts_created,
            'graph_nodes_upserted': self.graph_nodes_upserted,
            'graph_edges_upserted': self.graph_edges_upserted,
            'sync_errors': self.sync_errors,
        }


class RefreshWorkflow:
    """LangGraph workflow orchestrator for monthly refresh."""

    def __init__(self, org_repo, official_repo, policy_repo, release_repo, graphify_client):
        """Initialize workflow with repositories and Graphify client.

        Args:
            org_repo: OrganizationRepository instance
            official_repo: OfficialRepository instance
            policy_repo: PolicyRepository instance
            release_repo: PressReleaseRepository instance
            graphify_client: GraphifyClient instance
        """
        self.org_repo = org_repo
        self.official_repo = official_repo
        self.policy_repo = policy_repo
        self.release_repo = release_repo
        self.graphify = graphify_client
        self.graph = None
        self._build_graph()

    def _build_graph(self) -> None:
        """Build the LangGraph state graph."""
        if StateGraph is None:
            # Manual fallback: just define node functions
            self.nodes = {
                'discover': self.discover_organizations,
                'link_policies': self.link_policies,
                'link_pib': self.link_pib_activity,
                'sync': self.sync_to_graphify,
                'complete': self.on_complete,
            }
            self.edges = [
                ('discover', 'link_policies'),
                ('link_policies', 'link_pib'),
                ('link_pib', 'sync'),
                ('sync', 'complete'),
            ]
        else:
            self.graph = StateGraph(RefreshState)

            self.graph.add_node("discover", self.discover_organizations)
            self.graph.add_node("link_policies", self.link_policies)
            self.graph.add_node("link_pib", self.link_pib_activity)
            self.graph.add_node("sync", self.sync_to_graphify)
            self.graph.add_node("complete", self.on_complete)

            self.graph.add_edge("discover", "link_policies")
            self.graph.add_edge("link_policies", "link_pib")
            self.graph.add_edge("link_pib", "sync")
            self.graph.add_edge("sync", "complete")

            self.graph.set_entry_point("discover")

    def discover_organizations(self, state: RefreshState) -> RefreshState:
        """Phase 1: Discover organizations from igod and ministries.

        This would orchestrate:
        - igod_crawl.py (BFS seed pages → 431 listings)
        - igod_org_details.py (134 detail pages → T1 officials)
        - ministry_whoswho.py (tier-2 deep scrape → T2 officials)
        """
        try:
            # In production, call the actual scraper modules
            # For now, read from cached CSV data
            all_orgs = self.org_repo.find_all()
            all_officials_t1 = self.official_repo.find_all()
            all_officials_t2 = [o for o in all_officials_t1 if o.source == "ministry"]

            state.discovered_orgs = len(all_orgs)
            state.discovered_officials_t1 = len([o for o in all_officials_t1 if o.source == "igod"])
            state.discovered_officials_t2 = len(all_officials_t2)
            state.phase = RefreshPhase.LINKAGE

            print(f"[DISCOVER] Found {state.discovered_orgs} orgs, {state.discovered_officials_t1} T1, {state.discovered_officials_t2} T2")
            return state
        except Exception as e:
            state.sync_errors.append(f"Discovery failed: {str(e)}")
            state.phase = RefreshPhase.FAILED
            return state

    def link_policies(self, state: RefreshState) -> RefreshState:
        """Phase 2a: Link open policies to ministry contacts.

        Joins digital-twin-for-ipa open instruments to owning ministry's top-5 officials.
        """
        try:
            all_policies = self.policy_repo.find_all()
            open_policies = self.policy_repo.find_open()

            state.linked_policies = len(open_policies)

            # For each open policy, find top 3 officials in owning ministry
            for policy in open_policies:
                top_officials = self.official_repo.find_top_by_rank(policy.organization_id, limit=3)
                state.policy_contacts_created += len(top_officials)

            print(f"[LINKAGE] Linked {state.linked_policies} open policies to {state.policy_contacts_created} official contacts")
            return state
        except Exception as e:
            state.sync_errors.append(f"Policy linkage failed: {str(e)}")
            state.phase = RefreshPhase.FAILED
            return state

    def link_pib_activity(self, state: RefreshState) -> RefreshState:
        """Phase 2b: Link PIB press releases to ministry contacts.

        Joins 6-year PIB ministry activity to top-3 contacts per ministry.
        """
        try:
            # In production, load pib_index.sqlite and link
            all_releases = self.release_repo.find_all()

            state.linked_pib_releases = len(all_releases)

            # For each ministry with PIB releases, find top 3 officials
            ministry_ids = set(r.organization_id.value for r in all_releases)
            for ministry_id_str in ministry_ids:
                from ..domain.value_objects import OrganizationId
                ministry_id = OrganizationId(ministry_id_str)
                top_officials = self.official_repo.find_top_by_rank(ministry_id, limit=3)
                state.pib_contacts_created += len(top_officials)

            print(f"[LINKAGE] Linked {state.linked_pib_releases} PIB releases to {state.pib_contacts_created} official contacts")
            return state
        except Exception as e:
            state.sync_errors.append(f"PIB linkage failed: {str(e)}")
            state.phase = RefreshPhase.FAILED
            return state

    def sync_to_graphify(self, state: RefreshState) -> RefreshState:
        """Phase 3: Sync all entities to Graphify knowledge graph.

        Upserts nodes and edges for:
        - Organizations (nodes)
        - Officials (nodes + EMPLOYS edges)
        - Policies (nodes + OFFERS edges)
        - PressReleases (nodes + PUBLISHED edges)
        """
        try:
            # Upsert organizations
            for org in self.org_repo.find_all():
                self.graphify.upsert_node(
                    'Organization',
                    org.org_id.value,
                    {
                        'name': org.name,
                        'branch': org.location.branch,
                        'state': org.location.state,
                        'category': org.category,
                        'website': org.contact_info.website,
                    }
                )
                state.graph_nodes_upserted += 1

            # Upsert officials and EMPLOYS edges
            for official in self.official_repo.find_all():
                self.graphify.upsert_node(
                    'Official',
                    official.official_id.value,
                    {
                        'name': official.name,
                        'designation': official.designation.title,
                        'rank': official.designation.rank,
                        'email': official.contact_info.email,
                        'phones': official.contact_info.phone,
                    }
                )
                state.graph_nodes_upserted += 1

                self.graphify.upsert_edge(
                    'Organization', official.organization_id.value,
                    'EMPLOYS',
                    'Official', official.official_id.value,
                    {'rank': official.designation.rank}
                )
                state.graph_edges_upserted += 1

            # Upsert policies and OFFERS edges
            for policy in self.policy_repo.find_all():
                self.graphify.upsert_node(
                    'Policy',
                    policy.policy_id.value,
                    {
                        'instrument': policy.instrument,
                        'status': policy.status.value,
                        'tier': policy.tier,
                    }
                )
                state.graph_nodes_upserted += 1

                self.graphify.upsert_edge(
                    'Organization', policy.organization_id.value,
                    'OFFERS',
                    'Policy', policy.policy_id.value,
                    {'status': policy.status.value}
                )
                state.graph_edges_upserted += 1

            # Upsert press releases and PUBLISHED edges
            for release in self.release_repo.find_all():
                self.graphify.upsert_node(
                    'PressRelease',
                    release.release_id,
                    {
                        'date': release.date.isoformat(),
                        'title': release.title,
                        'url': release.url,
                    }
                )
                state.graph_nodes_upserted += 1

                self.graphify.upsert_edge(
                    'Organization', release.organization_id.value,
                    'PUBLISHED',
                    'PressRelease', release.release_id,
                )
                state.graph_edges_upserted += 1

            # Update sync timestamp
            self.graphify.set_metadata("official_sync_timestamp", datetime.utcnow().isoformat())

            print(f"[SYNC] Upserted {state.graph_nodes_upserted} nodes, {state.graph_edges_upserted} edges")
            return state
        except Exception as e:
            state.sync_errors.append(f"Graph sync failed: {str(e)}")
            state.phase = RefreshPhase.FAILED
            return state

    def on_complete(self, state: RefreshState) -> RefreshState:
        """Final phase: Mark refresh as complete."""
        if state.phase == RefreshPhase.FAILED:
            print(f"[COMPLETE] Refresh failed with {len(state.sync_errors)} errors")
        else:
            state.phase = RefreshPhase.COMPLETE
            print(f"[COMPLETE] Refresh successful. Stats: {state.to_dict()}")
        return state

    def run(self) -> RefreshState:
        """Execute the refresh workflow."""
        state = RefreshState(phase=RefreshPhase.DISCOVERY)

        if self.graph:
            # Use LangGraph executor
            runnable = self.graph.compile()
            final_state = runnable.invoke(state)
            return final_state
        else:
            # Manual fallback: execute nodes in sequence
            current = state
            for node_name, next_node_name in self.edges:
                node_func = self.nodes[node_name]
                current = node_func(current)
                if current.phase == RefreshPhase.FAILED:
                    break
            # Run the final complete node
            current = self.nodes['complete'](current)
            return current


def create_refresh_workflow(org_repo, official_repo, policy_repo, release_repo, graphify_client):
    """Factory function to create and return a refresh workflow."""
    return RefreshWorkflow(org_repo, official_repo, policy_repo, release_repo, graphify_client)
