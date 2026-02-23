from datetime import datetime

from core.strategy_factory.lifecycle.contracts import StrategyLifecycleState
from core.strategy_factory.lifecycle.audit import build_lifecycle_transition_audit


def test_lifecycle_audit_is_deterministic():
    ts = datetime(2025, 1, 1)

    audit1 = build_lifecycle_transition_audit(
        strategy_dna="STRAT-001",
        from_state=StrategyLifecycleState.RESEARCH,
        to_state=StrategyLifecycleState.PAPER,
        created_at=ts,
    )

    audit2 = build_lifecycle_transition_audit(
        strategy_dna="STRAT-001",
        from_state=StrategyLifecycleState.RESEARCH,
        to_state=StrategyLifecycleState.PAPER,
        created_at=ts,
    )

    assert audit1 == audit2


def test_lifecycle_audit_fingerprint_present():
    ts = datetime(2025, 1, 1)

    audit = build_lifecycle_transition_audit(
        strategy_dna="STRAT-002",
        from_state=StrategyLifecycleState.LIVE,
        to_state=StrategyLifecycleState.DEGRADED,
        created_at=ts,
    )

    assert audit.decision_fingerprint
