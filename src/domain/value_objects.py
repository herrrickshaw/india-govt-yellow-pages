"""Value Objects for the yellow pages domain."""
import re
from dataclasses import dataclass
from typing import Optional, List


@dataclass(frozen=True)
class OrganizationId:
    """Immutable ID for an organization (igod org id or generated)."""
    value: str

    def __post_init__(self):
        if not self.value or len(self.value.strip()) == 0:
            raise ValueError("OrganizationId cannot be empty")


@dataclass(frozen=True)
class OfficialId:
    """Immutable ID for an official (UUID or generated)."""
    value: str

    def __post_init__(self):
        if not self.value or len(self.value.strip()) == 0:
            raise ValueError("OfficialId cannot be empty")


@dataclass(frozen=True)
class PolicyId:
    """Immutable ID for a policy (from digital-twin-for-ipa)."""
    value: str

    def __post_init__(self):
        if not self.value or len(self.value.strip()) == 0:
            raise ValueError("PolicyId cannot be empty")


@dataclass(frozen=True)
class ContactInfo:
    """Immutable contact details."""
    address: Optional[str] = None
    phone: Optional[str] = None
    fax: Optional[str] = None
    email: Optional[str] = None
    website: Optional[str] = None
    room_number: Optional[str] = None

    def __post_init__(self):
        if self.email and not self._is_valid_email(self.email):
            raise ValueError(f"Invalid email format: {self.email}")
        if self.website and not self._is_valid_url(self.website):
            raise ValueError(f"Invalid website URL: {self.website}")

    @staticmethod
    def _is_valid_email(email: str) -> bool:
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))

    @staticmethod
    def _is_valid_url(url: str) -> bool:
        pattern = r'^https?://.+'
        return bool(re.match(pattern, url))


@dataclass(frozen=True)
class Designation:
    """Immutable designation with rank tier."""
    title: str
    rank: int  # 1 = Minister, 2 = Secretary, 3 = AS, 4 = JS, 5 = Director

    RANK_MAP = {
        "minister": 1,
        "principal secretary": 2,
        "additional secretary": 3,
        "joint secretary": 4,
        "director": 5,
        "secretary": 2,
    }

    def __post_init__(self):
        if not self.title or len(self.title.strip()) == 0:
            raise ValueError("Designation title cannot be empty")
        if not 1 <= self.rank <= 5:
            raise ValueError("Rank must be between 1 and 5")

    @classmethod
    def from_title(cls, title: str) -> "Designation":
        """Infer rank from designation title."""
        title_lower = title.lower()
        for key, rank in cls.RANK_MAP.items():
            if key in title_lower:
                return cls(title=title, rank=rank)
        return cls(title=title, rank=5)  # Default to Director


@dataclass(frozen=True)
class Location:
    """Immutable organization location."""
    branch: str  # ug/sg/apx/jud/leg/int
    state: str  # State/UT code

    VALID_BRANCHES = {"ug", "sg", "apx", "jud", "leg", "int"}

    def __post_init__(self):
        if self.branch not in self.VALID_BRANCHES:
            raise ValueError(f"Invalid branch: {self.branch}. Must be one of {self.VALID_BRANCHES}")
        if not self.state or len(self.state.strip()) == 0:
            raise ValueError("State cannot be empty")
