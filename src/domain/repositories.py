"""Repository interfaces (Abstract Base Classes)."""
from abc import ABC, abstractmethod
from typing import List, Optional

from .aggregates import Organization, Official, Policy, PressRelease
from .value_objects import OrganizationId, OfficialId, PolicyId


class OrganizationRepository(ABC):
    """Repository for Organization aggregates."""

    @abstractmethod
    def find_by_id(self, org_id: OrganizationId) -> Optional[Organization]:
        """Find organization by ID."""
        pass

    @abstractmethod
    def find_by_name(self, name: str) -> Optional[Organization]:
        """Find organization by canonical name (exact match)."""
        pass

    @abstractmethod
    def find_by_branch(self, branch: str) -> List[Organization]:
        """Find all organizations in a branch (ug/sg/apx/jud/leg/int)."""
        pass

    @abstractmethod
    def find_by_state(self, state: str) -> List[Organization]:
        """Find all organizations in a state/UT."""
        pass

    @abstractmethod
    def find_all(self) -> List[Organization]:
        """Retrieve all organizations."""
        pass

    @abstractmethod
    def save(self, org: Organization) -> None:
        """Persist an organization."""
        pass

    @abstractmethod
    def delete(self, org_id: OrganizationId) -> None:
        """Delete an organization (soft-delete)."""
        pass


class OfficialRepository(ABC):
    """Repository for Official aggregates."""

    @abstractmethod
    def find_by_id(self, official_id: OfficialId) -> Optional[Official]:
        """Find official by ID."""
        pass

    @abstractmethod
    def find_by_email(self, email: str) -> List[Official]:
        """Find officials by email."""
        pass

    @abstractmethod
    def find_by_name(self, name: str) -> List[Official]:
        """Find officials by name (substring search)."""
        pass

    @abstractmethod
    def find_by_organization(self, org_id: OrganizationId) -> List[Official]:
        """Find all officials in an organization."""
        pass

    @abstractmethod
    def find_by_designation(self, designation_title: str) -> List[Official]:
        """Find officials by designation title."""
        pass

    @abstractmethod
    def find_by_state(self, state: str) -> List[Official]:
        """Find officials in organizations located in a state/UT."""
        pass

    @abstractmethod
    def find_top_by_rank(self, org_id: OrganizationId, limit: int = 5) -> List[Official]:
        """Find top N officials in an organization, ordered by rank (seniority)."""
        pass

    @abstractmethod
    def find_all(self) -> List[Official]:
        """Retrieve all officials."""
        pass

    @abstractmethod
    def save(self, official: Official) -> None:
        """Persist an official."""
        pass

    @abstractmethod
    def delete(self, official_id: OfficialId) -> None:
        """Delete an official (soft-delete)."""
        pass


class PolicyRepository(ABC):
    """Repository for Policy aggregates."""

    @abstractmethod
    def find_by_id(self, policy_id: PolicyId) -> Optional[Policy]:
        """Find policy by ID."""
        pass

    @abstractmethod
    def find_by_instrument(self, instrument: str) -> Optional[Policy]:
        """Find policy by instrument name (exact match)."""
        pass

    @abstractmethod
    def find_open(self) -> List[Policy]:
        """Find all open policies."""
        pass

    @abstractmethod
    def find_by_ministry(self, org_id: OrganizationId) -> List[Policy]:
        """Find all policies offered by a ministry."""
        pass

    @abstractmethod
    def find_by_status(self, status_str: str) -> List[Policy]:
        """Find policies by status ('open', 'closed', 'in-force')."""
        pass

    @abstractmethod
    def find_by_tier(self, tier: str) -> List[Policy]:
        """Find policies by tier (e.g., 'National', 'State')."""
        pass

    @abstractmethod
    def find_all(self) -> List[Policy]:
        """Retrieve all policies."""
        pass

    @abstractmethod
    def save(self, policy: Policy) -> None:
        """Persist a policy."""
        pass

    @abstractmethod
    def delete(self, policy_id: PolicyId) -> None:
        """Delete a policy (soft-delete)."""
        pass


class PressReleaseRepository(ABC):
    """Repository for PressRelease aggregates (PIB activity)."""

    @abstractmethod
    def find_by_id(self, release_id: str) -> Optional[PressRelease]:
        """Find press release by ID."""
        pass

    @abstractmethod
    def find_by_ministry(self, org_id: OrganizationId) -> List[PressRelease]:
        """Find all releases published by a ministry."""
        pass

    @abstractmethod
    def find_by_date_range(self, start_date, end_date) -> List[PressRelease]:
        """Find releases within a date range."""
        pass

    @abstractmethod
    def find_by_6year_trend(self) -> dict:
        """Find release counts grouped by year for last 6 years.
        Returns: {2021: 42, 2022: 38, ...}
        """
        pass

    @abstractmethod
    def find_by_90day_recency(self, org_id: OrganizationId) -> int:
        """Count releases published in last 90 days for a ministry."""
        pass

    @abstractmethod
    def find_all(self) -> List[PressRelease]:
        """Retrieve all releases."""
        pass

    @abstractmethod
    def save(self, release: PressRelease) -> None:
        """Persist a press release."""
        pass

    @abstractmethod
    def delete(self, release_id: str) -> None:
        """Delete a press release (soft-delete)."""
        pass
