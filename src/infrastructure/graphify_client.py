"""Graphify knowledge graph client wrapper."""
import json
from typing import Any, Dict, List, Optional
from datetime import datetime


class GraphifyClient:
    """Client for interacting with Graphify knowledge graph backend."""

    def __init__(self, graph_file: str = "~/.graphify/global-graph.json"):
        """Initialize Graphify client.

        Args:
            graph_file: Path to the global Graphify graph file
        """
        self.graph_file = graph_file
        self._nodes: Dict[str, Dict[str, Any]] = {}
        self._edges: List[Dict[str, Any]] = []
        self._metadata: Dict[str, Any] = {
            'official_sync_timestamp': None,
            'policy_sync_timestamp': None,
            'pib_sync_timestamp': None,
        }
        self._load_graph()

    def _load_graph(self) -> None:
        """Load graph from file (stub for now; real implementation fetches from Graphify API)."""
        # In production, this would load from the Graphify server or local graph file
        # For now, we initialize with empty state
        pass

    def upsert_node(self, node_type: str, node_id: str, properties: Dict[str, Any]) -> bool:
        """Upsert a node into the graph."""
        full_id = f"{node_type.lower()}:{node_id}" if ':' not in node_id else node_id

        self._nodes[full_id] = {
            'id': full_id,
            'type': node_type,
            'properties': {
                **properties,
                'updated_at': datetime.utcnow().isoformat(),
            }
        }
        return True

    def upsert_edge(self, source_type: str, source_id: str,
                    edge_type: str,
                    target_type: str, target_id: str,
                    properties: Optional[Dict[str, Any]] = None) -> bool:
        """Upsert an edge into the graph."""
        source_full_id = f"{source_type.lower()}:{source_id}" if ':' not in source_id else source_id
        target_full_id = f"{target_type.lower()}:{target_id}" if ':' not in target_id else target_id

        edge_key = f"{source_full_id}-{edge_type}-{target_full_id}"

        # Check if edge already exists
        for existing in self._edges:
            if (existing.get('source') == source_full_id and
                existing.get('target') == target_full_id and
                existing.get('type') == edge_type):
                # Update existing edge
                existing['properties'] = {
                    **(properties or {}),
                    'updated_at': datetime.utcnow().isoformat(),
                }
                return True

        # Add new edge
        self._edges.append({
            'source': source_full_id,
            'target': target_full_id,
            'type': edge_type,
            'properties': {
                **(properties or {}),
                'created_at': datetime.utcnow().isoformat(),
            }
        })
        return True

    def get_node(self, node_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a node by ID."""
        return self._nodes.get(node_id)

    def get_neighbors(self, node_id: str, edge_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get all neighbors of a node (optionally filtered by edge type)."""
        neighbors = []
        for edge in self._edges:
            if edge['source'] == node_id:
                if edge_type is None or edge['type'] == edge_type:
                    target = self._nodes.get(edge['target'])
                    if target:
                        neighbors.append({
                            'node': target,
                            'edge_type': edge['type'],
                            'edge_properties': edge.get('properties', {})
                        })
        return neighbors

    def get_incoming_edges(self, node_id: str, edge_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get all incoming edges to a node."""
        incoming = []
        for edge in self._edges:
            if edge['target'] == node_id:
                if edge_type is None or edge['type'] == edge_type:
                    source = self._nodes.get(edge['source'])
                    if source:
                        incoming.append({
                            'node': source,
                            'edge_type': edge['type'],
                            'edge_properties': edge.get('properties', {})
                        })
        return incoming

    def query(self, query_str: str) -> List[Dict[str, Any]]:
        """Execute a graph query (simplified; in production uses Graphify DSL).

        Supported query patterns:
        - "MATCH (n:NodeType {property: value})" — find nodes by type and property
        - "MATCH (n)-[EDGE_TYPE]->(m)" — traverse edges
        """
        # This is a stub. Real implementation parses Graphify DSL and executes.
        # For now, return empty results.
        return []

    def get_metadata(self, key: str) -> Optional[Any]:
        """Retrieve metadata (e.g., last sync timestamp)."""
        return self._metadata.get(key)

    def set_metadata(self, key: str, value: Any) -> None:
        """Set metadata."""
        self._metadata[key] = value

    def get_stats(self) -> Dict[str, Any]:
        """Get graph statistics."""
        # Count nodes by type
        node_counts = {}
        for node in self._nodes.values():
            node_type = node['type']
            node_counts[node_type] = node_counts.get(node_type, 0) + 1

        # Count edges by type
        edge_counts = {}
        for edge in self._edges:
            edge_type = edge['type']
            edge_counts[edge_type] = edge_counts.get(edge_type, 0) + 1

        return {
            'total_nodes': len(self._nodes),
            'total_edges': len(self._edges),
            'node_counts_by_type': node_counts,
            'edge_counts_by_type': edge_counts,
            'last_update': datetime.utcnow().isoformat(),
        }

    def export_nodes(self) -> List[Dict[str, Any]]:
        """Export all nodes."""
        return list(self._nodes.values())

    def export_edges(self) -> List[Dict[str, Any]]:
        """Export all edges."""
        return self._edges

    def commit(self) -> bool:
        """Commit changes to persistent storage (if applicable)."""
        # In production, this would persist to Graphify or a local graph file
        return True
