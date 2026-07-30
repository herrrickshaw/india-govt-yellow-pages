"""Concrete repository implementations backed by Graphify and CSV data."""
import csv
from pathlib import Path
from typing import List, Optional, Dict
from datetime import datetime, timedelta

from ..domain.aggregates import Organization, Official, Policy, PressRelease, PolicyStatus
from ..domain.repositories import (
    OrganizationRepository, OfficialRepository, PolicyRepository, PressReleaseRepository
)
from ..domain.value_objects import (
    OrganizationId, OfficialId, PolicyId, ContactInfo, Designation, Location
)
from .graphify_client import GraphifyClient


class GraphifyOrganizationRepository(OrganizationRepository):
    """Organization repository backed by Graphify graph."""

    def __init__(self, graphify: GraphifyClient, data_dir: Path = None):
        self.graphify = graphify
        self.data_dir = data_dir or Path(__file__).resolve().parent.parent.parent / "data"
        self._load_organizations_from_csv()

    def _load_organizations_from_csv(self) -> None:
        """Load organizations from CSV into memory cache."""
        self._orgs_by_id: Dict[str, Organization] = {}
        self._orgs_by_name: Dict[str, Organization] = {}

        org_index_path = self.data_dir / "organizations_index.csv"
        org_contacts_path = self.data_dir / "org_contacts.csv"

        if not org_index_path.exists():
            return

        # Load base organization data
        org_details = {}
        with org_index_path.open(encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                org_id = row.get('id') or row.get('igod_id')
                org_details[org_id] = row

        # Load contact data
        contacts_by_org = {}
        if org_contacts_path.exists():
            with org_contacts_path.open(encoding='utf-8-sig') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    org_id = row.get('organization_id') or row.get('id')
                    contacts_by_org[org_id] = row

        # Build organizations
        for org_id, details in org_details.items():
            contact_data = contacts_by_org.get(org_id, {})
            try:
                org = Organization(
                    org_id=OrganizationId(org_id),
                    name=details.get('name', ''),
                    location=Location(
                        branch=details.get('branch', 'ug'),
                        state=details.get('state', 'IN')
                    ),
                    contact_info=ContactInfo(
                        address=contact_data.get('address'),
                        phone=contact_data.get('phone'),
                        fax=contact_data.get('fax'),
                        email=contact_data.get('email'),
                        website=details.get('website') or contact_data.get('website'),
                    ),
                    category=details.get('category'),
                )
                self._orgs_by_id[org_id] = org
                self._orgs_by_name[org.name.lower()] = org
            except ValueError:
                # Skip invalid organizations
                pass

    def find_by_id(self, org_id: OrganizationId) -> Optional[Organization]:
        return self._orgs_by_id.get(org_id.value)

    def find_by_name(self, name: str) -> Optional[Organization]:
        return self._orgs_by_name.get(name.lower())

    def find_by_branch(self, branch: str) -> List[Organization]:
        return [o for o in self._orgs_by_id.values() if o.location.branch == branch]

    def find_by_state(self, state: str) -> List[Organization]:
        return [o for o in self._orgs_by_id.values() if o.location.state == state]

    def find_all(self) -> List[Organization]:
        return list(self._orgs_by_id.values())

    def save(self, org: Organization) -> None:
        """Persist organization to graph."""
        self._orgs_by_id[org.org_id.value] = org
        self._orgs_by_name[org.name.lower()] = org

        # Upsert to Graphify
        self.graphify.upsert_node(
            'Organization',
            org.org_id.value,
            {
                'name': org.name,
                'branch': org.location.branch,
                'state': org.location.state,
                'category': org.category,
                'website': org.contact_info.website,
                'contact_email': org.contact_info.email,
                'source': org.source,
            }
        )

    def delete(self, org_id: OrganizationId) -> None:
        """Soft-delete organization."""
        if org_id.value in self._orgs_by_id:
            org = self._orgs_by_id.pop(org_id.value)
            del self._orgs_by_name[org.name.lower()]


class GraphifyOfficialRepository(OfficialRepository):
    """Official repository backed by Graphify graph."""

    def __init__(self, graphify: GraphifyClient, data_dir: Path = None):
        self.graphify = graphify
        self.data_dir = data_dir or Path(__file__).resolve().parent.parent.parent / "data"
        self._load_officials_from_csv()

    def _load_officials_from_csv(self) -> None:
        """Load officials from CSV into memory cache."""
        self._officials_by_id: Dict[str, Official] = {}
        self._officials_by_email: Dict[str, List[Official]] = {}
        self._officials_by_name: Dict[str, List[Official]] = {}
        self._officials_by_org: Dict[str, List[Official]] = {}

        # Try both igod and ministry officials
        for csv_file in ["officials.csv", "ministry_officials.csv"]:
            path = self.data_dir / csv_file
            if not path.exists():
                continue

            with path.open(encoding='utf-8-sig') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    try:
                        official_id = OfficialId(row.get('id') or f"{row.get('name')}-{row.get('email')}")
                        designation = Designation.from_title(row.get('designation', 'Officer'))
                        org_id = OrganizationId(row.get('organization_id', 'unknown'))

                        official = Official(
                            official_id=official_id,
                            name=row.get('name', ''),
                            designation=designation,
                            contact_info=ContactInfo(
                                address=row.get('office_address'),
                                phone=row.get('phones'),
                                email=row.get('email'),
                                room_number=row.get('room_number'),
                            ),
                            organization_id=org_id,
                            source=row.get('source', 'igod'),
                        )
                        self._officials_by_id[official_id.value] = official

                        # Index by email
                        if official.contact_info.email:
                            email = official.contact_info.email.lower()
                            if email not in self._officials_by_email:
                                self._officials_by_email[email] = []
                            self._officials_by_email[email].append(official)

                        # Index by name
                        name_key = official.name.lower()
                        if name_key not in self._officials_by_name:
                            self._officials_by_name[name_key] = []
                        self._officials_by_name[name_key].append(official)

                        # Index by organization
                        org_key = org_id.value
                        if org_key not in self._officials_by_org:
                            self._officials_by_org[org_key] = []
                        self._officials_by_org[org_key].append(official)
                    except (ValueError, KeyError):
                        # Skip invalid rows
                        pass

    def find_by_id(self, official_id: OfficialId) -> Optional[Official]:
        return self._officials_by_id.get(official_id.value)

    def find_by_email(self, email: str) -> List[Official]:
        return self._officials_by_email.get(email.lower(), [])

    def find_by_name(self, name: str) -> List[Official]:
        name_key = name.lower()
        results = []
        for key, officials in self._officials_by_name.items():
            if name_key in key or key in name_key:
                results.extend(officials)
        return results

    def find_by_organization(self, org_id: OrganizationId) -> List[Official]:
        return self._officials_by_org.get(org_id.value, [])

    def find_by_designation(self, designation_title: str) -> List[Official]:
        return [o for o in self._officials_by_id.values()
                if designation_title.lower() in o.designation.title.lower()]

    def find_by_state(self, state: str) -> List[Official]:
        # This would require joining with organizations; stub for now
        return []

    def find_top_by_rank(self, org_id: OrganizationId, limit: int = 5) -> List[Official]:
        """Find top N officials by rank (lower rank number = higher seniority)."""
        officials = self.find_by_organization(org_id)
        sorted_officials = sorted(officials, key=lambda o: o.designation.rank)
        return sorted_officials[:limit]

    def find_all(self) -> List[Official]:
        return list(self._officials_by_id.values())

    def save(self, official: Official) -> None:
        """Persist official to graph."""
        self._officials_by_id[official.official_id.value] = official

        # Upsert to Graphify
        self.graphify.upsert_node(
            'Official',
            official.official_id.value,
            {
                'name': official.name,
                'designation': official.designation.title,
                'rank': official.designation.rank,
                'email': official.contact_info.email,
                'phones': official.contact_info.phone,
                'office_address': official.contact_info.address,
                'source': official.source,
            }
        )
        self.graphify.upsert_edge(
            'Organization', official.organization_id.value,
            'EMPLOYS',
            'Official', official.official_id.value,
            {'rank': official.designation.rank}
        )

    def delete(self, official_id: OfficialId) -> None:
        """Soft-delete official."""
        if official_id.value in self._officials_by_id:
            del self._officials_by_id[official_id.value]


class GraphifyPolicyRepository(PolicyRepository):
    """Policy repository backed by Graphify graph."""

    def __init__(self, graphify: GraphifyClient, data_dir: Path = None):
        self.graphify = graphify
        self.data_dir = data_dir or Path(__file__).resolve().parent.parent.parent / "data"
        self._load_policies_from_csv()

    def _load_policies_from_csv(self) -> None:
        """Load policies from CSV into memory cache."""
        self._policies_by_id: Dict[str, Policy] = {}
        self._policies_by_ministry: Dict[str, List[Policy]] = {}

        path = self.data_dir / "policy_contacts.csv"
        if not path.exists():
            return

        with path.open(encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    policy_id = PolicyId(row.get('id') or row.get('instrument'))
                    status_str = row.get('status', 'open').lower()
                    status = PolicyStatus.OPEN if 'open' in status_str else PolicyStatus.CLOSED

                    policy = Policy(
                        policy_id=policy_id,
                        instrument=row.get('instrument', ''),
                        organization_id=OrganizationId(row.get('ministry_id', 'unknown')),
                        tier=row.get('tier', 'National'),
                        status=status,
                        description=row.get('description'),
                        source_url=row.get('source_url'),
                    )
                    self._policies_by_id[policy_id.value] = policy

                    # Index by ministry
                    ministry_key = policy.organization_id.value
                    if ministry_key not in self._policies_by_ministry:
                        self._policies_by_ministry[ministry_key] = []
                    self._policies_by_ministry[ministry_key].append(policy)
                except (ValueError, KeyError):
                    pass

    def find_by_id(self, policy_id: PolicyId) -> Optional[Policy]:
        return self._policies_by_id.get(policy_id.value)

    def find_by_instrument(self, instrument: str) -> Optional[Policy]:
        for policy in self._policies_by_id.values():
            if policy.instrument.lower() == instrument.lower():
                return policy
        return None

    def find_open(self) -> List[Policy]:
        return [p for p in self._policies_by_id.values() if p.status == PolicyStatus.OPEN]

    def find_by_ministry(self, org_id: OrganizationId) -> List[Policy]:
        return self._policies_by_ministry.get(org_id.value, [])

    def find_by_status(self, status_str: str) -> List[Policy]:
        status = PolicyStatus.OPEN if 'open' in status_str.lower() else PolicyStatus.CLOSED
        return [p for p in self._policies_by_id.values() if p.status == status]

    def find_by_tier(self, tier: str) -> List[Policy]:
        return [p for p in self._policies_by_id.values() if p.tier.lower() == tier.lower()]

    def find_all(self) -> List[Policy]:
        return list(self._policies_by_id.values())

    def save(self, policy: Policy) -> None:
        self._policies_by_id[policy.policy_id.value] = policy
        self.graphify.upsert_node(
            'Policy',
            policy.policy_id.value,
            {
                'instrument': policy.instrument,
                'status': policy.status.value,
                'tier': policy.tier,
                'description': policy.description,
            }
        )
        self.graphify.upsert_edge(
            'Organization', policy.organization_id.value,
            'OFFERS',
            'Policy', policy.policy_id.value,
            {'status': policy.status.value}
        )

    def delete(self, policy_id: PolicyId) -> None:
        if policy_id.value in self._policies_by_id:
            del self._policies_by_id[policy_id.value]


class GraphifyPressReleaseRepository(PressReleaseRepository):
    """Press release repository backed by Graphify graph."""

    def __init__(self, graphify: GraphifyClient, data_dir: Path = None):
        self.graphify = graphify
        self.data_dir = data_dir or Path(__file__).resolve().parent.parent.parent / "data"
        self._load_releases_from_csv()

    def _load_releases_from_csv(self) -> None:
        """Load PIB releases from CSV into memory cache."""
        self._releases_by_id: Dict[str, PressRelease] = {}
        self._releases_by_ministry: Dict[str, List[PressRelease]] = {}

        path = self.data_dir / "pib_ministry_contacts.csv"
        if not path.exists():
            return

        with path.open(encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    release_id = row.get('id') or row.get('pib_id')
                    date_str = row.get('date', '')
                    release_date = datetime.fromisoformat(date_str) if date_str else datetime.utcnow()

                    release = PressRelease(
                        release_id=release_id,
                        organization_id=OrganizationId(row.get('ministry_id', 'unknown')),
                        date=release_date,
                        title=row.get('title', ''),
                        url=row.get('url', ''),
                        category=row.get('category'),
                    )
                    self._releases_by_id[release_id] = release

                    # Index by ministry
                    ministry_key = release.organization_id.value
                    if ministry_key not in self._releases_by_ministry:
                        self._releases_by_ministry[ministry_key] = []
                    self._releases_by_ministry[ministry_key].append(release)
                except (ValueError, KeyError):
                    pass

    def find_by_id(self, release_id: str) -> Optional[PressRelease]:
        return self._releases_by_id.get(release_id)

    def find_by_ministry(self, org_id: OrganizationId) -> List[PressRelease]:
        return self._releases_by_ministry.get(org_id.value, [])

    def find_by_date_range(self, start_date, end_date) -> List[PressRelease]:
        return [r for r in self._releases_by_id.values()
                if start_date <= r.date <= end_date]

    def find_by_6year_trend(self) -> dict:
        """Group releases by year for last 6 years."""
        counts = {}
        now = datetime.utcnow()
        for year in range(now.year - 5, now.year + 1):
            counts[year] = 0

        for release in self._releases_by_id.values():
            year = release.date.year
            if year in counts:
                counts[year] += 1

        return counts

    def find_by_90day_recency(self, org_id: OrganizationId) -> int:
        """Count releases in last 90 days."""
        threshold = datetime.utcnow() - timedelta(days=90)
        releases = self.find_by_ministry(org_id)
        return sum(1 for r in releases if r.date >= threshold)

    def find_all(self) -> List[PressRelease]:
        return list(self._releases_by_id.values())

    def save(self, release: PressRelease) -> None:
        self._releases_by_id[release.release_id] = release
        self.graphify.upsert_node(
            'PressRelease',
            release.release_id,
            {
                'date': release.date.isoformat(),
                'title': release.title,
                'url': release.url,
                'category': release.category,
            }
        )
        self.graphify.upsert_edge(
            'Organization', release.organization_id.value,
            'PUBLISHED',
            'PressRelease', release.release_id,
            {'category': release.category}
        )

    def delete(self, release_id: str) -> None:
        if release_id in self._releases_by_id:
            del self._releases_by_id[release_id]
