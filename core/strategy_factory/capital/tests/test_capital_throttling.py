# core/strategy_factory/capital/tests/test_capital_throttling.py

from datetime import datetime, timezone, timedelta

from core.strategy_factory.capital.throttling import (
    decide_capital_throttle,
)
from core.strategy_factory.capital.throttling_models import (
    CapitalThrottleDecision,
)


UTC = timezone.utc


def _now():
    return datetime(2025, 1, 10, tzinfo=UTC)


def test_throttle_allows_when_no_prior_allocation():
    decision = decide_capital_throttle(
        last_allocation_at=None,
        cooldown_seconds=3600,
        now=_now(),
    )

    assert isinstance(decision, CapitalThrottleDecision)
    assert decision.allowed is True
    assert "allowed" in decision.reason.lower()


def test_throttle_allows_after_cooldown_elapsed():
    decision = decide_capital_throttle(
        last_allocation_at=_now() - timedelta(hours=2),
        cooldown_seconds=3600,
        now=_now(),
    )

    assert decision.allowed is True


def test_throttle_blocks_within_cooldown():
    decision = decide_capital_throttle(
        last_allocation_at=_now() - timedelta(minutes=10),
        cooldown_seconds=3600,
        now=_now(),
    )

    assert decision.allowed is False
    assert "cooldown" in decision.reason.lower()


def test_throttle_is_deterministic():
    args = dict(
        last_allocation_at=_now() - timedelta(minutes=30),
        cooldown_seconds=3600,
        now=_now(),
    )

    d1 = decide_capital_throttle(**args)
    d2 = decide_capital_throttle(**args)

    assert d1 == d2


def test_throttle_does_not_mutate_inputs():
    last = _now() - timedelta(minutes=30)
    snapshot = last

    decide_capital_throttle(
        last_allocation_at=last,
        cooldown_seconds=3600,
        now=_now(),
    )

    assert last == snapshot
