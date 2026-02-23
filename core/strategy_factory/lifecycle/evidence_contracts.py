# core/strategy_factory/lifecycle/evidence_contracts.py

from dataclasses import dataclass
from typing import Optional

from core.strategy_factory.lifecycle.contracts import StrategyLifecycleState


# ======================================================
# 🧾 LIFECYCLE TRANSITION EVIDENCE (AUDIT-ONLY)
# ======================================================

@dataclass(frozen=True)
class LifecycleTransitionEvidence:
    """
    Immutable evidence record for a lifecycle transition.

    IMPORTANT:
    - Observational only
    - Does NOT validate transitions
    - Does NOT mutate lifecycle state
    - Safe for replay, audit, and governance review
    """

    # Identity
    strategy_id: str

    # Transition
    from_state: StrategyLifecycleState
    to_state: StrategyLifecycleState

    # Optional explanatory metadata (pure, additive)
    reason: Optional[str] = None

    # Determinism anchor (caller-provided)
    transition_id: Optional[str] = None
