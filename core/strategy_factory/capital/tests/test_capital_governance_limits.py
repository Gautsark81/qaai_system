from datetime import datetime
import copy

import pytest

from core.strategy_factory.capital.governance_limits import (
    decide_capital_governance_limits,
)
from core.strategy_factory.capital.governance_models import (
    CapitalGovernanceDecision,
    CapitalGovernanceLimits,
)


# ============================================================
# Helpers
# ============================================================

def _limits(
    *,
    global_cap: float = 1_000_000,
    per_strategy_cap: float = 200_000,
    max_concentration_pct: float = 0.25,
):
    return CapitalGovernanceLimits(
        global_cap=global_cap,
        per_strategy_cap=per_strategy_cap,
        max_concentration_pct=max_concentration_pct,
    )


# ============================================================
# C4.1-A-T1 — Allow when within all limits
# ============================================================

def test_governance_allows_when_within_limits():
    decision = decide_capital_governance_limits(
        strategy_dna="STRAT-001",
        requested_capital=50_000,
        strategy_current_capital=100_000,
        global_capital_used=400_000,
        limits=_limits(),
    )

    assert decision.allowed is True
    assert "allowed" in decision.reason.lower()


# ============================================================
# C4.1-A-T2 — Reject when global cap exceeded
# ============================================================

def test_governance_rejects_when_global_cap_exceeded():
    decision = decide_capital_governance_limits(
        strategy_dna="STRAT-002",
        requested_capital=200_000,
        strategy_current_capital=50_000,
        global_capital_used=900_000,
        limits=_limits(global_cap=1_000_000),
    )

    assert decision.allowed is False
    assert "global cap" in decision.reason.lower()


# ============================================================
# C4.1-A-T3 — Reject when per-strategy cap exceeded
# ============================================================

def test_governance_rejects_when_strategy_cap_exceeded():
    decision = decide_capital_governance_limits(
        strategy_dna="STRAT-003",
        requested_capital=150_000,
        strategy_current_capital=100_000,
        global_capital_used=300_000,
        limits=_limits(per_strategy_cap=200_000),
    )

    assert decision.allowed is False
    assert "per-strategy" in decision.reason.lower()


# ============================================================
# C4.1-A-T4 — Reject when concentration exceeded
# ============================================================

def test_governance_rejects_when_concentration_exceeded():
    decision = decide_capital_governance_limits(
        strategy_dna="STRAT-004",
        requested_capital=100_000,
        strategy_current_capital=150_000,
        global_capital_used=300_000,
        limits=_limits(
            global_cap=500_000,
            max_concentration_pct=0.40,
        ),
    )

    # New strategy total would be 250k / 500k = 50%
    assert decision.allowed is False
    assert "concentration" in decision.reason.lower()


# ============================================================
# C4.1-A-T5 — Deterministic decision
# ============================================================

def test_governance_decision_is_deterministic():
    args = dict(
        strategy_dna="STRAT-005",
        requested_capital=25_000,
        strategy_current_capital=50_000,
        global_capital_used=200_000,
        limits=_limits(),
    )

    d1 = decide_capital_governance_limits(**args)
    d2 = decide_capital_governance_limits(**args)

    assert d1 == d2


# ============================================================
# C4.1-A-T6 — Inputs are not mutated
# ============================================================

def test_governance_does_not_mutate_inputs():
    limits = _limits()
    snapshot = copy.deepcopy(limits)

    decide_capital_governance_limits(
        strategy_dna="STRAT-006",
        requested_capital=10_000,
        strategy_current_capital=20_000,
        global_capital_used=100_000,
        limits=limits,
    )

    assert limits == snapshot


# ============================================================
# C4.1-A-T7 — Explicit reject reason required
# ============================================================

def test_governance_reject_has_explicit_reason():
    decision = decide_capital_governance_limits(
        strategy_dna="STRAT-007",
        requested_capital=500_000,
        strategy_current_capital=0,
        global_capital_used=600_000,
        limits=_limits(global_cap=1_000_000),
    )

    assert decision.allowed is False
    assert isinstance(decision.reason, str)
    assert len(decision.reason.strip()) > 0
