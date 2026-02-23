# tests/execution/test_cold_restart_reconciliation.py

import pytest

from core.execution.restart_guard import (
    RestartGuard,
    RestartDecision,
)


# ------------------------------------------------------------
# 1️⃣ Perfect Match
# ------------------------------------------------------------

def test_restart_allows_when_positions_match():
    guard = RestartGuard()

    internal = {
        "RELIANCE": 100,
        "INFY": 50,
    }

    broker = {
        "RELIANCE": 100,
        "INFY": 50,
    }

    decision = guard.validate_positions(
        internal_positions=internal,
        broker_positions=broker,
    )

    assert decision.allowed is True
    assert decision.freeze is False


# ------------------------------------------------------------
# 2️⃣ Missing Broker Position
# ------------------------------------------------------------

def test_restart_freezes_when_broker_has_extra_position():
    guard = RestartGuard()

    internal = {
        "RELIANCE": 100,
    }

    broker = {
        "RELIANCE": 100,
        "INFY": 50,
    }

    decision = guard.validate_positions(
        internal_positions=internal,
        broker_positions=broker,
    )

    assert decision.freeze is True
    assert "MISMATCH" in decision.reason


# ------------------------------------------------------------
# 3️⃣ Internal Missing Position
# ------------------------------------------------------------

def test_restart_freezes_when_internal_missing_position():
    guard = RestartGuard()

    internal = {
        "RELIANCE": 100,
        "INFY": 50,
    }

    broker = {
        "RELIANCE": 100,
    }

    decision = guard.validate_positions(
        internal_positions=internal,
        broker_positions=broker,
    )

    assert decision.freeze is True


# ------------------------------------------------------------
# 4️⃣ Quantity Drift
# ------------------------------------------------------------

def test_restart_freezes_when_quantity_differs():
    guard = RestartGuard()

    internal = {
        "RELIANCE": 100,
    }

    broker = {
        "RELIANCE": 120,
    }

    decision = guard.validate_positions(
        internal_positions=internal,
        broker_positions=broker,
    )

    assert decision.freeze is True


# ------------------------------------------------------------
# 5️⃣ Empty Both
# ------------------------------------------------------------

def test_restart_allows_when_both_empty():
    guard = RestartGuard()

    decision = guard.validate_positions(
        internal_positions={},
        broker_positions={},
    )

    assert decision.allowed is True