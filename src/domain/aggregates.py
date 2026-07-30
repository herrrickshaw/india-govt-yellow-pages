"""Domain aggregate roots."""
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Set
from enum import Enum

from .value_objects import (
    OrganizationId, OfficialId, PolicyId, ContactInfo, Designation, Location
)


class PolicyStatus(Enum):
    """Policy status enumeration."""
    OPEN = "open"
    CLOSED = "closed"
    IN_FORCE = "in-force"


@dataclass
class Organization:
    """Organization aggregate root."""
    org_id: OrganizationId
    name: str
    location: Location
    contact_info: ContactInfo
    category: Optional[str] = None
    source: str = "igod"
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def __post_init__(self):
        if not self.name or len(self.name.strip()) == 0:
            raise ValueError("Organization name cannot be empty")
        if len(self.name) < 3:
            raise ValueError("Organization name must be at least 3 characters")

    def update_contact_info(self, contact_info: ContactInfo) -> None:
        """Update contact information and mark as updated."""
        self.contact_info = contact_info
        self.updated_at = datetime.utcnow()

    def to_graph_node(self) -> dict:
        """Convert to Graphify node representation."""
        return {
            'id': f"org:{self.org_id.value}",
            'type': 'Organization',
            'properties': {
                'name': self.name,
                'branch': self.location.branch,
                'state': self.location.state,
                'category': self.category,
                'website': self.contact_info.website,
                'contact_email': self.contact_info.email,
                'source': self.source,
                'created_at': self.created_at.isoformat(),
                'updated_at': self.updated_at.isoformat(),
            }
        }


@dataclass
class Official:
    """Official aggregate root."""
    official_id: OfficialId
    name: str
    designation: Designation
    contact_info: ContactInfo
    organization_id: OrganizationId
    source: str = "igod"
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def __post_init__(self):
        if not self.name or len(self.name.strip()) == 0:
            raise ValueError("Official name cannot be empty")
        if len(self.name) < 3:
            raise ValueError("Official name must be at least 3 characters")
        # Exclude rank markers
        rank_markers = {"minister", "secretary", "director", "officer", "staff"}
        if self.name.lower() in rank_markers:
            raise ValueError(f"Official name cannot be just a rank marker: {self.name}")

    def update_contact_info(self, contact_info: ContactInfo) -> None:
        """Update contact information and mark as updated."""
        self.contact_info = contact_info
        self.updated_at = datetime.utcnow()

    def to_graph_node(self) -> dict:
        """Convert to Graphify node representation."""
        return {
            'id': f"official:{self.official_id.value}",
            'type': 'Official',
            'properties': {
                'name': self.name,
                'designation': self.designation.title,
                'rank': self.designation.rank,
                'email': self.contact_info.email,
                'phones': self.contact_info.phone,
                'office_address': self.contact_info.address,
                'room_number': self.contact_info.room_number,
                'source': self.source,
                'created_at': self.created_at.isoformat(),
                'updated_at': self.updated_at.isoformat(),
            }
        }

    def to_graph_edge(self, org_id: OrganizationId) -> dict:
        """Create EMPLOYS edge from Organization to Official."""
        return {
            'source': f"org:{org_id.value}",
            'target': f"official:{self.official_id.value}",
            'type': 'EMPLOYS',
            'properties': {
                'rank': self.designation.rank,
                'source': self.source,
            }
        }


@dataclass
class Policy:
    """Policy aggregate root."""
    policy_id: PolicyId
    instrument: str  # Policy name
    organization_id: OrganizationId  # Owning ministry
    tier: str  # e.g., "National", "State"
    status: PolicyStatus
    description: Optional[str] = None
    source_url: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def __post_init__(self):
        if not self.instrument or len(self.instrument.strip()) == 0:
            raise ValueError("Policy instrument cannot be empty")
        if len(self.instrument) < 3:
            raise ValueError("Policy instrument must be at least 3 characters")

    def update_status(self, status: PolicyStatus) -> None:
        """Update policy status and mark as updated."""
        self.status = status
        self.updated_at = datetime.utcnow()

    def to_graph_node(self) -> dict:
        """Convert to Graphify node representation."""
        return {
            'id': f"policy:{self.policy_id.value}",
            'type': 'Policy',
            'properties': {
                'instrument': self.instrument,
                'tier': self.tier,
                'status': self.status.value,
                'description': self.description,
                'source_url': self.source_url,
                'created_at': self.created_at.isoformat(),
                'updated_at': self.updated_at.isoformat(),
            }
        }

    def to_graph_edge(self, org_id: OrganizationId) -> dict:
        """Create OFFERS edge from Organization to Policy."""
        return {
            'source': f"org:{org_id.value}",
            'target': f"policy:{self.policy_id.value}",
            'type': 'OFFERS',
            'properties': {
                'status': self.status.value,
                'tier': self.tier,
            }
        }


@dataclass
class PressRelease:
    """Press release aggregate root (PIB activity)."""
    release_id: str
    organization_id: OrganizationId
    date: datetime
    title: str
    url: str
    category: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)

    def __post_init__(self):
        if not self.release_id or len(self.release_id.strip()) == 0:
            raise ValueError("Release ID cannot be empty")
        if not self.title or len(self.title.strip()) == 0:
            raise ValueError("Release title cannot be empty")

    def to_graph_node(self) -> dict:
        """Convert to Graphify node representation."""
        return {
            'id': f"pib:{self.release_id}",
            'type': 'PressRelease',
            'properties': {
                'date': self.date.isoformat(),
                'title': self.title,
                'url': self.url,
                'category': self.category,
                'created_at': self.created_at.isoformat(),
            }
        }

    def to_graph_edge(self, org_id: OrganizationId) -> dict:
        """Create PUBLISHED edge from Organization to PressRelease."""
        return {
            'source': f"org:{org_id.value}",
            'target': f"pib:{self.release_id}",
            'type': 'PUBLISHED',
            'properties': {
                'category': self.category,
            }
        }
