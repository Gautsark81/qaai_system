from datetime import datetime, timezone

import pytest

from core.strategy_factory.capital.engine import run_capital_engine
from core.strategy_factory.capital.governance_models import CapitalGovernanceLimits
from core.strategy_factory.capital.throttling_models import CapitalThrottleDecision
from core.strategy_factory.capital.context import CapitalContext


# -------------------------------------------------------------------
# Helpers
# -------------------------------------------------------------------

FIXED_NOW = datetime(2025, 1, 1, tzinfo=timezone.utc)


def _context():
    return CapitalContext(
        strategy_current_capital=100_000,
        global_capital_used=300_000,
    )


def _allow_limits():
    return CapitalGovernanceLimits(
        global_cap=1_000_000,
        max_per_strategy=300_000,
        max_concentration_pct=0.50,
    )


# -------------------------------------------------------------------
# Tests
# -------------------------------------------------------------------

def test_throttle_blocks_allocation(monkeypatch):
    called = {"allocation": False}

    def _fake_allocation(*args, **kwargs):
        called["allocation"] = True

    def _fake_throttle(*args, **kwargs):
        return CapitalThrottleDecision(
            allowed=False,
            reason="Cooldown active",
            retry_after_seconds=600,
        )

    monkeypatch.setattr(
        "core.strategy_factory.capital.allocation_policy.apply_allocation_policy",
        _fake_allocation,
    )

    monkeypatch.setattr(
        "core.strategy_factory.capital.throttling.evaluate_capital_throttle",
        _fake_throttle,
    )

    result = run_capital_engine(
        strategy_dna="STRAT-T1",
        requested_capital=50_000,
        limits=_allow_limits(),
        context=_context(),
        now=FIXED_NOW,
    )

    assert called["allocation"] is False
    assert result.throttle.allowed is False
    assert "cooldown" in result.throttle.reason.lower()
    assert result.allocation is None


def test_throttle_blocks_eligibility(monkeypatch):
    called = {"eligibility": False}

    def _fake_eligibility(*args, **kwargs):
        called["eligibility"] = True

    def _fake_throttle(*args, **kwargs):
        return CapitalThrottleDecision(
            allowed=False,
            reason="Cooldown active",
            retry_after_seconds=300,
        )

    monkeypatch.setattr(
        "core.strategy_factory.capital.decision.decide_capital_eligibility",
        _fake_eligibility,
    )

    monkeypatch.setattr(
        "core.strategy_factory.capital.throttling.evaluate_capital_throttle",
        _fake_throttle,
    )

    run_capital_engine(
        strategy_dna="STRAT-T2",
        requested_capital=40_000,
        limits=_allow_limits(),
        context=_context(),
        now=FIXED_NOW,
    )

    assert called["eligibility"] is False


def test_throttle_allows_allocation(monkeypatch):
    called = {"allocation": False}

    def _fake_allocation(*args, **kwargs):
        called["allocation"] = True
        return None

    def _fake_throttle(*args, **kwargs):
        return CapitalThrottleDecision(
            allowed=True,
            reason="Throttle passed",
            retry_after_seconds=None,
        )

    monkeypatch.setattr(
        "core.strategy_factory.capital.allocation_policy.apply_allocation_policy",
        _fake_allocation,
    )

    monkeypatch.setattr(
        "core.strategy_factory.capital.throttling.evaluate_capital_throttle",
        _fake_throttle,
    )

    run_capital_engine(
        strategy_dna="STRAT-T3",
        requested_capital=25_000,
        limits=_allow_limits(),
        context=_context(),
        now=FIXED_NOW,
    )

    assert called["allocation"] is True


def test_throttle_evaluated_after_governance(monkeypatch):
    order = []

    def _fake_governance(*args, **kwargs):
        order.append("governance")
        from core.strategy_factory.capital.governance_models import (
            CapitalGovernanceDecision,
        )

        return CapitalGovernanceDecision(
            allowed=True,
            reason="Allowed",
        )

    def _fake_throttle(*args, **kwargs):
        order.append("throttle")
        return CapitalThrottleDecision(
            allowed=False,
            reason="Cooldown",
            retry_after_seconds=60,
        )

    monkeypatch.setattr(
        "core.strategy_factory.capital.governance_limits.decide_capital_governance_limits",
        _fake_governance,
    )

    monkeypatch.setattr(
        "core.strategy_factory.capital.throttling.evaluate_capital_throttle",
        _fake_throttle,
    )

    run_capital_engine(
        strategy_dna="STRAT-T4",
        requested_capital=10_000,
        limits=_allow_limits(),
        context=_context(),
        now=FIXED_NOW,
    )

    assert order == ["governance", "throttle"]


def test_throttle_audit_is_deterministic(monkeypatch):
    def _fake_throttle(*args, **kwargs):
        return CapitalThrottleDecision(
            allowed=False,
            reason="Cooldown active",
            retry_after_seconds=120,
        )

    monkeypatch.setattr(
        "core.strategy_factory.capital.throttling.evaluate_capital_throttle",
        _fake_throttle,
    )

    r1 = run_capital_engine(
        strategy_dna="STRAT-T5",
        requested_capital=15_000,
        limits=_allow_limits(),
        context=_context(),
        now=FIXED_NOW,
    )

    r2 = run_capital_engine(
        strategy_dna="STRAT-T5",
        requested_capital=15_000,
        limits=_allow_limits(),
        context=_context(),
        now=FIXED_NOW,
    )

    assert r1.throttle == r2.throttle
