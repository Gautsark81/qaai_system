from dataclasses import dataclass
from typing import Dict


@dataclass(frozen=True)
class GovernanceSnapshot:
    """
    Immutable representation of governance state.
    """
    rules_hash: str
    thresholds: Dict[str, float]
    version: str


@dataclass(frozen=True)
class GovernanceDriftSignal:
    """
    Advisory-only governance drift signal.
    """
    drift_type: str
    previous_value: str
    current_value: str
