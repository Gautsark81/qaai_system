# core/evidence/replay_contracts.py

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Tuple


@dataclass(frozen=True)
class ReplayFrame:
    """
    Deterministic snapshot of system-relevant decisions at a point in time.
    """
    timestamp: datetime

    # Keyed by strategy_id
    capital_allocations: Dict[str, float]

    # Keyed by strategy_id
    governance_states: Dict[str, str]

    # Regime / system context
    market_regime: str
    regime_confidence: float


@dataclass(frozen=True)
class ReplayDiff:
    """
    Structural difference between two replay frames.
    """
    from_timestamp: datetime
    to_timestamp: datetime

    added: Dict[str, Dict]
    removed: Dict[str, Dict]
    changed: Dict[str, Tuple[Dict, Dict]]
