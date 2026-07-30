"""REST API for querying the yellow pages knowledge graph."""
from typing import List, Optional, Dict, Any
from dataclasses import asdict
from datetime import datetime


class QueryAPI:
    """Query API for searching and traversing the knowledge graph."""

    def __init__(self, org_repo, official_repo, policy_repo, release_repo, graphify_client):
        """Initialize API with repositories."""
        self.org_repo = org_repo
        self.official_repo = official_repo
        self.policy_repo = policy_repo
        self.release_repo = release_repo
        self.graphify = graphify_client

    # ============ Officials API ============

    def search_officials(self, name: Optional[str] = None,
                        email: Optional[str] = None,
                        ministry_id: Optional[str] = None,
                        state: Optional[str] = None,
                        designation: Optional[str] = None) -> List[Dict[str, Any]]:
        """Search for officials by multiple criteria."""
        results = []

        if email:
            results.extend(self.official_repo.find_by_email(email))
        elif name:
            results.extend(self.official_repo.find_by_name(name))
        elif ministry_id:
            from ..domain.value_objects import OrganizationId
            results.extend(self.official_repo.find_by_organization(OrganizationId(ministry_id)))
        elif designation:
            results.extend(self.official_repo.find_by_designation(designation))
        elif state:
            results.extend(self.official_repo.find_by_state(state))
        else:
            results.extend(self.official_repo.find_all())

        # Convert to dicts
        return [self._official_to_dict(o) for o in results]

    def get_official(self, official_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific official by ID."""
        from ..domain.value_objects import OfficialId
        official = self.official_repo.find_by_id(OfficialId(official_id))
        return self._official_to_dict(official) if official else None

    def _official_to_dict(self, official) -> Dict[str, Any]:
        """Convert Official aggregate to dict."""
        return {
            'id': official.official_id.value,
            'name': official.name,
            'designation': official.designation.title,
            'rank': official.designation.rank,
            'email': official.contact_info.email,
            'phones': official.contact_info.phone,
            'office_address': official.contact_info.address,
            'room_number': official.contact_info.room_number,
            'organization_id': official.organization_id.value,
            'source': official.source,
        }

    # ============ Organizations API ============

    def search_organizations(self, name: Optional[str] = None,
                            branch: Optional[str] = None,
                            state: Optional[str] = None) -> List[Dict[str, Any]]:
        """Search for organizations by criteria."""
        results = []

        if name:
            org = self.org_repo.find_by_name(name)
            if org:
                results.append(org)
        elif branch:
            results.extend(self.org_repo.find_by_branch(branch))
        elif state:
            results.extend(self.org_repo.find_by_state(state))
        else:
            results.extend(self.org_repo.find_all())

        return [self._org_to_dict(o) for o in results]

    def get_organization(self, org_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific organization by ID."""
        from ..domain.value_objects import OrganizationId
        org = self.org_repo.find_by_id(OrganizationId(org_id))
        return self._org_to_dict(org) if org else None

    def get_organization_officials(self, org_id: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Get top officials in an organization (by rank)."""
        from ..domain.value_objects import OrganizationId
        officials = self.official_repo.find_top_by_rank(OrganizationId(org_id), limit)
        return [self._official_to_dict(o) for o in officials]

    def get_organization_policies(self, org_id: str) -> List[Dict[str, Any]]:
        """Get all policies offered by an organization."""
        from ..domain.value_objects import OrganizationId
        policies = self.policy_repo.find_by_ministry(OrganizationId(org_id))
        return [self._policy_to_dict(p) for p in policies]

    def _org_to_dict(self, org) -> Dict[str, Any]:
        """Convert Organization aggregate to dict."""
        return {
            'id': org.org_id.value,
            'name': org.name,
            'branch': org.location.branch,
            'state': org.location.state,
            'category': org.category,
            'address': org.contact_info.address,
            'phone': org.contact_info.phone,
            'email': org.contact_info.email,
            'website': org.contact_info.website,
        }

    # ============ Policies API ============

    def search_policies(self, instrument: Optional[str] = None,
                       ministry_id: Optional[str] = None,
                       status: Optional[str] = None,
                       tier: Optional[str] = None) -> List[Dict[str, Any]]:
        """Search for policies by criteria."""
        results = []

        if instrument:
            policy = self.policy_repo.find_by_instrument(instrument)
            if policy:
                results.append(policy)
        elif ministry_id:
            from ..domain.value_objects import OrganizationId
            results.extend(self.policy_repo.find_by_ministry(OrganizationId(ministry_id)))
        elif status:
            results.extend(self.policy_repo.find_by_status(status))
        elif tier:
            results.extend(self.policy_repo.find_by_tier(tier))
        else:
            results.extend(self.policy_repo.find_all())

        return [self._policy_to_dict(p) for p in results]

    def get_policy(self, policy_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific policy by ID."""
        from ..domain.value_objects import PolicyId
        policy = self.policy_repo.find_by_id(PolicyId(policy_id))
        return self._policy_to_dict(policy) if policy else None

    def get_policy_contacts(self, policy_id: str, limit: int = 3) -> List[Dict[str, Any]]:
        """Get top officials as contacts for a policy."""
        from ..domain.value_objects import PolicyId, OrganizationId
        policy = self.policy_repo.find_by_id(PolicyId(policy_id))
        if not policy:
            return []
        officials = self.official_repo.find_top_by_rank(policy.organization_id, limit)
        return [self._official_to_dict(o) for o in officials]

    def _policy_to_dict(self, policy) -> Dict[str, Any]:
        """Convert Policy aggregate to dict."""
        return {
            'id': policy.policy_id.value,
            'instrument': policy.instrument,
            'ministry_id': policy.organization_id.value,
            'tier': policy.tier,
            'status': policy.status.value,
            'description': policy.description,
            'source_url': policy.source_url,
        }

    # ============ Press Releases API ============

    def get_ministry_pib_activity(self, org_id: str) -> Dict[str, Any]:
        """Get PIB activity stats for a ministry."""
        from ..domain.value_objects import OrganizationId
        org_id_obj = OrganizationId(org_id)

        releases = self.release_repo.find_by_ministry(org_id_obj)
        trend_6y = self.release_repo.find_by_6year_trend()
        recency_90d = self.release_repo.find_by_90day_recency(org_id_obj)

        return {
            'ministry_id': org_id,
            'total_releases': len(releases),
            'releases_90d': recency_90d,
            'trend_6years': trend_6y,
            'latest_release': max([r.date for r in releases], default=None).isoformat() if releases else None,
            'releases': [self._release_to_dict(r) for r in releases][:10],  # Top 10
        }

    def _release_to_dict(self, release) -> Dict[str, Any]:
        """Convert PressRelease aggregate to dict."""
        return {
            'id': release.release_id,
            'date': release.date.isoformat(),
            'title': release.title,
            'url': release.url,
            'category': release.category,
        }

    # ============ Graph Traversal API ============

    def traverse_graph(self, start_node_id: str, depth: int = 2) -> Dict[str, Any]:
        """Traverse graph starting from a node up to specified depth.

        Returns all reachable nodes and edges from the starting point.
        """
        visited = set()
        nodes = {}
        edges = []

        def traverse(node_id: str, current_depth: int) -> None:
            if node_id in visited or current_depth > depth:
                return

            visited.add(node_id)
            node_data = self.graphify.get_node(node_id)
            if node_data:
                nodes[node_id] = node_data

            neighbors = self.graphify.get_neighbors(node_id)
            for neighbor_info in neighbors:
                neighbor_node = neighbor_info['node']
                edge_type = neighbor_info['edge_type']
                edges.append({
                    'source': node_id,
                    'target': neighbor_node['id'],
                    'type': edge_type,
                })
                traverse(neighbor_node['id'], current_depth + 1)

        traverse(start_node_id, 0)

        return {
            'root': start_node_id,
            'nodes': nodes,
            'edges': edges,
            'node_count': len(nodes),
            'edge_count': len(edges),
        }

    # ============ Stats API ============

    def get_stats(self) -> Dict[str, Any]:
        """Get overall statistics."""
        all_orgs = self.org_repo.find_all()
        all_officials = self.official_repo.find_all()
        all_policies = self.policy_repo.find_all()
        all_releases = self.release_repo.find_all()

        graph_stats = self.graphify.get_stats()

        return {
            'organizations': len(all_orgs),
            'officials': len(all_officials),
            'policies': len(all_policies),
            'press_releases': len(all_releases),
            'graph_stats': graph_stats,
            'timestamp': datetime.utcnow().isoformat(),
        }
