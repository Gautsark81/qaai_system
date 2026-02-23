from datetime import datetime, timedelta

import pytest

from core.strategy_factory.capital.throttling import (
    evaluate_capital_throttle,
    get_throttle_audit_ledger,
)


# ==========================================================
# Test Utilities
# ==========================================================


def _reset_ledger():
    """
    Safe reset inside test boundary only.
    """
    ledger = get_throttle_audit_ledger()
    ledger._events.clear()


# ==========================================================
# 1️⃣ Event Emitted on Throttle
# ==========================================================


def test_event_emitted_on_throttle_block():
    _reset_ledger()

    now = datetime(2026, 1, 1, 10, 0, 0)
    last = now - timedelta(seconds=10)

    evaluate_capital_throttle(
        strategy_dna="alpha",
        requested_capital=100.0,
        last_allocation_at=last,
        cooldown_seconds=60,
        now=now,
    )

    ledger = get_throttle_audit_ledger()
    events = ledger.events

    assert len(events) == 1

    event = events[0]

    assert event.strategy_dna == "alpha"
    assert event.allowed is False
    assert event.was_throttled is True
    assert event.retry_after_seconds == 50
    assert event.evaluated_at == now


# ==========================================================
# 2️⃣ Event Emitted on Allow
# ==========================================================


def test_event_emitted_on_allow():
    _reset_ledger()

    now = datetime(2026, 1, 1, 10, 0, 0)

    evaluate_capital_throttle(
        strategy_dna="beta",
        requested_capital=200.0,
        last_allocation_at=None,
        cooldown_seconds=60,
        now=now,
    )

    ledger = get_throttle_audit_ledger()
    events = ledger.events

    assert len(events) == 1

    event = events[0]

    assert event.strategy_dna == "beta"
    assert event.allowed is True
    assert event.was_throttled is False
    assert event.retry_after_seconds is None


# ==========================================================
# 3️⃣ Ledger Is Append-Only
# ==========================================================


def test_ledger_is_append_only():
    _reset_ledger()

    now = datetime(2026, 1, 1, 10, 0, 0)

    evaluate_capital_throttle(
        strategy_dna="alpha",
        requested_capital=100,
        last_allocation_at=None,
        cooldown_seconds=60,
        now=now,
    )

    evaluate_capital_throttle(
        strategy_dna="alpha",
        requested_capital=100,
        last_allocation_at=now,
        cooldown_seconds=60,
        now=now,
    )

    ledger = get_throttle_audit_ledger()

    assert len(ledger.events) == 2


# ==========================================================
# 4️⃣ Ledger Is Read-Only From Outside
# ==========================================================


def test_ledger_events_returns_copy():
    _reset_ledger()

    now = datetime(2026, 1, 1, 10, 0, 0)

    evaluate_capital_throttle(
        strategy_dna="alpha",
        requested_capital=100,
        last_allocation_at=None,
        cooldown_seconds=60,
        now=now,
    )

    ledger = get_throttle_audit_ledger()

    external_view = ledger.events
    external_view.append("malicious")

    # Ledger must not be mutated
    assert len(ledger.events) == 1


# ==========================================================
# 5️⃣ Snapshot State Serializable
# ==========================================================


def test_snapshot_state_is_serializable():
    _reset_ledger()

    now = datetime(2026, 1, 1, 10, 0, 0)

    evaluate_capital_throttle(
        strategy_dna="gamma",
        requested_capital=150,
        last_allocation_at=None,
        cooldown_seconds=60,
        now=now,
    )

    ledger = get_throttle_audit_ledger()

    state = ledger.snapshot_state()

    assert isinstance(state, list)
    assert isinstance(state[0], dict)

    assert state[0]["strategy_dna"] == "gamma"
    assert "evaluated_at" in state[0]


# ==========================================================
# 6️⃣ Deterministic Behavior (No Wall Clock Leakage)
# ==========================================================


def test_throttle_is_deterministic():
    _reset_ledger()

    now = datetime(2026, 1, 1, 10, 0, 0)

    decision1 = evaluate_capital_throttle(
        strategy_dna="alpha",
        requested_capital=100,
        last_allocation_at=None,
        cooldown_seconds=60,
        now=now,
    )

    _reset_ledger()

    decision2 = evaluate_capital_throttle(
        strategy_dna="alpha",
        requested_capital=100,
        last_allocation_at=None,
        cooldown_seconds=60,
        now=now,
    )

    assert decision1.allowed == decision2.allowed
    assert decision1.reason == decision2.reason


# ==========================================================
# 7️⃣ Cooldown Boundary Condition
# ==========================================================


def test_cooldown_boundary_allows_exact_limit():
    _reset_ledger()

    now = datetime(2026, 1, 1, 10, 1, 0)
    last = datetime(2026, 1, 1, 10, 0, 0)

    decision = evaluate_capital_throttle(
        strategy_dna="alpha",
        requested_capital=100,
        last_allocation_at=last,
        cooldown_seconds=60,
        now=now,
    )

    assert decision.allowed is True


# ==========================================================
# 8️⃣ Negative Cooldown Rejected
# ==========================================================


def test_negative_cooldown_rejected():
    _reset_ledger()

    now = datetime(2026, 1, 1, 10, 0, 0)

    with pytest.raises(ValueError):
        evaluate_capital_throttle(
            strategy_dna="alpha",
            requested_capital=100,
            last_allocation_at=None,
            cooldown_seconds=-1,
            now=now,
        )