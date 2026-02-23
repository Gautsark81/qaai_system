from dataclasses import dataclass
from typing import Optional, Dict


@dataclass(frozen=True)
class OperatorSnapshot:
    """
    Immutable operator-facing snapshot explaining
    why the system is currently active.

    This object:
    - is human-readable
    - is regulator-readable
    - is replay-safe
    - has NO execution authority
    """

    timestamp: int
    mode: str  # shadow / paper / live
    strategy_id: Optional[str]
    last_operator_intent: str
    governance_summary: Dict[str, str]
    capital_summary: Dict[str, str]
    notes: Optional[str] = None
