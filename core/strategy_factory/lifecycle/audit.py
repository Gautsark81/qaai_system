from __future__ import annotations

from datetime import datetime

from core.strategy_factory.lifecycle.contracts import StrategyLifecycleState
from core.strategy_factory.lifecycle.models import LifecycleTransitionAuditRecord
from core.strategy_factory.lifecycle.fingerprints import fingerprint_transition


def build_lifecycle_transition_audit(
    *,
    strategy_dna: str,
    from_state: StrategyLifecycleState,
    to_state: StrategyLifecycleState,
    created_at: datetime,
) -> LifecycleTransitionAuditRecord:
    """
    Build an immutable audit record for a lifecycle transition.

    Pure, deterministic, explainability-only.
    """

    return LifecycleTransitionAuditRecord(
        strategy_dna=strategy_dna,
        from_state=from_state,
        to_state=to_state,
        decision_fingerprint=fingerprint_transition(from_state, to_state),
        created_at=created_at,
    )
