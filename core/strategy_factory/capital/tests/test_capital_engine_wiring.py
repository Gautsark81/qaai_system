from datetime import datetime

from core.strategy_factory.capital.engine import run_capital_engine
from core.strategy_factory.capital.governance_models import (
    CapitalGovernanceLimits,
    CapitalGovernanceDecision,
)
from core.strategy_factory.capital.context import CapitalContext
from core.strategy_factory.capital.engine_models import CapitalEngineResult


# -------------------------------------------------------------------
# Helpers
# -------------------------------------------------------------------

def _context():
    """
    Must match the REAL CapitalContext contract in the repo.
    """
    return CapitalContext(
        strategy_current_capital=100_000,
        global_capital_used=400_000,
    )

def _allow_limits():
    return CapitalGovernanceLimits(
        global_cap=1_000_000,
        max_per_strategy=300_000,
        max_concentration_pct=0.50,
    )


def _deny_limits():
    return CapitalGovernanceLimits(
        global_cap=500_000,
        max_per_strategy=150_000,
        max_concentration_pct=0.20,
    )


# -------------------------------------------------------------------
# C4-W1-T1 — Governance denial blocks allocation entirely
# -------------------------------------------------------------------

def test_governance_denial_blocks_allocation(monkeypatch):
    called = {"allocation": False}

    def _fake_allocation(*args, **kwargs):
        called["allocation"] = True

    monkeypatch.setattr(
        "core.strategy_factory.capital.allocation_policy.apply_allocation_policy",
        _fake_allocation,
    )

    result = run_capital_engine(
        strategy_dna="STRAT-001",
        requested_capital=100_000,
        limits=_deny_limits(),
        context=_context(),
    )

    assert isinstance(result, CapitalEngineResult)
    assert result.governance.allowed is False
    assert result.allocation is None
    assert called["allocation"] is False


# -------------------------------------------------------------------
# C4-W1-T2 — Governance approval allows allocation path
# -------------------------------------------------------------------

def test_governance_allows_allocation(monkeypatch):
    called = {"allocation": False}

    def _fake_allocation(*args, **kwargs):
        called["allocation"] = True
        return None

    monkeypatch.setattr(
        "core.strategy_factory.capital.allocation_policy.apply_allocation_policy",
        _fake_allocation,
    )

    run_capital_engine(
        strategy_dna="STRAT-002",
        requested_capital=50_000,
        limits=_allow_limits(),
        context=_context(),
    )

    assert called["allocation"] is True


# -------------------------------------------------------------------
# C4-W1-T3 — Governance audit is always present
# -------------------------------------------------------------------

def test_governance_audit_always_present():
    result = run_capital_engine(
        strategy_dna="STRAT-003",
        requested_capital=20_000,
        limits=_allow_limits(),
        context=_context(),
    )

    assert result.governance is not None
    assert isinstance(result.governance, CapitalGovernanceDecision)
    assert isinstance(result.governance_audit.fingerprint, str)
    assert len(result.governance_audit.fingerprint) >= 16


# -------------------------------------------------------------------
# C4-W1-T4 — Deterministic engine output
# -------------------------------------------------------------------

def test_capital_engine_is_deterministic():
    r1 = run_capital_engine(
        strategy_dna="STRAT-004",
        requested_capital=40_000,
        limits=_allow_limits(),
        context=_context(),
    )

    r2 = run_capital_engine(
        strategy_dna="STRAT-004",
        requested_capital=40_000,
        limits=_allow_limits(),
        context=_context(),
    )

    assert r1 == r2


# -------------------------------------------------------------------
# C4-W1-T5 — Eligibility & allocation never evaluated on governance failure
# -------------------------------------------------------------------

def test_allocation_is_never_evaluated_on_governance_failure(monkeypatch):
    called = {"eligibility": False}

    def _fake_eligibility(*args, **kwargs):
        called["eligibility"] = True

    monkeypatch.setattr(
        "core.strategy_factory.capital.decision.decide_capital_eligibility",
        _fake_eligibility,
    )

    run_capital_engine(
        strategy_dna="STRAT-005",
        requested_capital=200_000,
        limits=_deny_limits(),
        context=_context(),
    )

    assert called["eligibility"] is False
