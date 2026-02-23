# core/institution/succession/models.py
from dataclasses import dataclass
from typing import Dict, Any


@dataclass(frozen=True)
class Steward:
    """
    Logical system steward (person or role).
    """
    steward_id: str
    name: str
    metadata: Dict[str, Any]


@dataclass(frozen=True)
class SuccessionEvent:
    """
    Audited handover of stewardship.
    """
    from_steward: Steward
    to_steward: Steward
    reason: str
