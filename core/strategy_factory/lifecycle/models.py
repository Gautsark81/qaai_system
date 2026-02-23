from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from core.strategy_factory.lifecycle.contracts import StrategyLifecycleState


@dataclass(frozen=True)
class LifecycleTransitionAuditRecord:
    """
    Immutable audit record for a lifecycle state transition.

    This artifact is explainability-only:
    - No behavior
    - No validation
    - No side effects

    It exists to provide lineage, reproducibility,
    and governance transparency.
    """

    # Strategy identity
    strategy_dna: str

    # Transition
    from_state: StrategyLifecycleState
    to_state: StrategyLifecycleState

    # Deterministic fingerprint proving transition intent
    decision_fingerprint: str

    # Explicitly injected timestamp
    created_at: datetime
