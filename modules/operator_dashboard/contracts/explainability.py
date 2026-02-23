from dataclasses import dataclass
from typing import Dict, Any


@dataclass(frozen=True)
class ExplainabilitySnapshot:
    """
    Immutable explainability projection for operator dashboard.

    Read-only.
    Deterministic.
    No execution authority.
    """

    strategy_traces: Dict[str, Any]
    system_notes: Dict[str, Any]
