# core/strategy_factory/capital/tests/test_promotion_gate.py

from datetime import datetime, timedelta

from core.strategy_factory.capital.throttling import (
    evaluate_capital_throttle,
    get_throttle_audit_ledger,
)
from core.strategy_factory.capital.promotion_gate import (
    evaluate_strategy_promotion,
)


def _reset_ledger():
    ledger = get_throttle_audit_ledger()
    ledger._events.clear()


def test_promotion_denied_if_no_history():
    _reset_ledger()

    result = evaluate_strategy_promotion(strategy_dna="alpha")

    assert not result.allowed
    assert result.discipline_score == 0.0
    assert result.total_events == 0


def test_promotion_allowed_with_clean_history():
    _reset_ledger()

    now = datetime.utcnow()

    for _ in range(5):
        evaluate_capital_throttle(
            strategy_dna="alpha",
            requested_capital=1000,
            last_allocation_at=None,
            cooldown_seconds=10,
            now=now,
        )

    result = evaluate_strategy_promotion(strategy_dna="alpha")

    assert result.allowed
    assert result.discipline_score == 1.0
    assert result.throttle_events == 0


def test_promotion_denied_if_discipline_low():
    _reset_ledger()

    now = datetime.utcnow()

    # First allowed
    evaluate_capital_throttle(
        strategy_dna="alpha",
        requested_capital=1000,
        last_allocation_at=None,
        cooldown_seconds=10,
        now=now,
    )

    # Force throttles
    last = now
    for _ in range(4):
        evaluate_capital_throttle(
            strategy_dna="alpha",
            requested_capital=1000,
            last_allocation_at=last,
            cooldown_seconds=100,
            now=now,
        )

    result = evaluate_strategy_promotion(strategy_dna="alpha")

    assert not result.allowed
    assert result.discipline_score < 0.8
    assert result.throttle_events > 0


def test_strategy_isolated_from_other_strategies():
    _reset_ledger()

    now = datetime.utcnow()

    # Alpha clean
    evaluate_capital_throttle(
        strategy_dna="alpha",
        requested_capital=1000,
        last_allocation_at=None,
        cooldown_seconds=10,
        now=now,
    )

    # Beta throttled
    evaluate_capital_throttle(
        strategy_dna="beta",
        requested_capital=1000,
        last_allocation_at=now,
        cooldown_seconds=100,
        now=now,
    )

    alpha_result = evaluate_strategy_promotion(strategy_dna="alpha")
    beta_result = evaluate_strategy_promotion(strategy_dna="beta")

    assert alpha_result.allowed
    assert not beta_result.allowed


def test_custom_thresholds():
    _reset_ledger()

    now = datetime.utcnow()

    # First allowed
    evaluate_capital_throttle(
        strategy_dna="alpha",
        requested_capital=1000,
        last_allocation_at=None,
        cooldown_seconds=10,
        now=now,
    )

    # Then throttled
    evaluate_capital_throttle(
        strategy_dna="alpha",
        requested_capital=1000,
        last_allocation_at=now,
        cooldown_seconds=100,
        now=now,
    )

    result = evaluate_strategy_promotion(
        strategy_dna="alpha",
        min_discipline_score=0.3,
        max_throttle_ratio=0.6,   # 🔥 MUST override this too
    )

    assert result.allowed
    assert result.discipline_score == 0.5