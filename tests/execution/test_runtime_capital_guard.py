# tests/execution/test_runtime_capital_guard.py

import pytest
from dataclasses import dataclass

from core.execution.runtime_capital_guard import (
    RuntimeCapitalGuard,
    CapitalGuardDecision,
)


@dataclass
class DummyEnvelope:
    global_cap: float
    strategy_cap: float
    symbol_cap: float


@dataclass
class DummyExposure:
    global_exposure: float
    strategy_exposure: float
    symbol_exposure: float


class DummyKillSwitch:
    def __init__(self):
        self._red = False

    def trigger(self):
        self._red = True

    def is_triggered(self):
        return self._red


def build_guard():
    return RuntimeCapitalGuard()


# ---------------------------------------------------------
# PRE-EXECUTION TESTS
# ---------------------------------------------------------

def test_pre_execution_allows_within_limits():
    guard = build_guard()

    decision = guard.validate_pre_execution(
        envelope=DummyEnvelope(100000, 50000, 20000),
        exposure=DummyExposure(20000, 10000, 5000),
        proposed_order_value=10000,
        kill_switch=None,
    )

    assert decision.allowed is True
    assert decision.freeze is False


def test_pre_execution_blocks_global_cap_breach():
    guard = build_guard()

    decision = guard.validate_pre_execution(
        envelope=DummyEnvelope(30000, 50000, 20000),
        exposure=DummyExposure(25000, 10000, 5000),
        proposed_order_value=10000,
        kill_switch=None,
    )

    assert decision.allowed is False
    assert decision.freeze is True
    assert "GLOBAL_CAP" in decision.reason


def test_pre_execution_blocks_strategy_cap_breach():
    guard = build_guard()

    decision = guard.validate_pre_execution(
        envelope=DummyEnvelope(100000, 15000, 20000),
        exposure=DummyExposure(20000, 14000, 5000),
        proposed_order_value=2000,
        kill_switch=None,
    )

    assert decision.allowed is False
    assert decision.freeze is True
    assert "STRATEGY_CAP" in decision.reason


def test_pre_execution_blocks_symbol_cap_breach():
    guard = build_guard()

    decision = guard.validate_pre_execution(
        envelope=DummyEnvelope(100000, 50000, 8000),
        exposure=DummyExposure(20000, 10000, 7000),
        proposed_order_value=2000,
        kill_switch=None,
    )

    assert decision.allowed is False
    assert decision.freeze is True
    assert "SYMBOL_CAP" in decision.reason


# ---------------------------------------------------------
# KILL SWITCH TEST
# ---------------------------------------------------------

def test_pre_execution_blocks_if_kill_switch_triggered():
    guard = build_guard()
    ks = DummyKillSwitch()
    ks.trigger()

    decision = guard.validate_pre_execution(
        envelope=DummyEnvelope(100000, 50000, 20000),
        exposure=DummyExposure(20000, 10000, 5000),
        proposed_order_value=10000,
        kill_switch=ks,
    )

    assert decision.allowed is False
    assert decision.freeze is True
    assert "KILL_SWITCH" in decision.reason


# ---------------------------------------------------------
# POST-FILL VALIDATION
# ---------------------------------------------------------

def test_post_fill_allows_valid_state():
    guard = build_guard()

    decision = guard.validate_post_fill(
        envelope=DummyEnvelope(100000, 50000, 20000),
        updated_exposure=DummyExposure(30000, 15000, 10000),
    )

    assert decision.allowed is True
    assert decision.freeze is False


def test_post_fill_freezes_on_global_drift():
    guard = build_guard()

    decision = guard.validate_post_fill(
        envelope=DummyEnvelope(30000, 50000, 20000),
        updated_exposure=DummyExposure(35000, 15000, 10000),
    )

    assert decision.allowed is False
    assert decision.freeze is True
    assert "GLOBAL_DRIFT" in decision.reason


# ---------------------------------------------------------
# RETRY VALIDATION
# ---------------------------------------------------------

def test_retry_requires_same_idempotency_key():
    guard = build_guard()

    decision = guard.validate_retry(
        original_key="abc",
        retry_key="xyz",
    )

    assert decision.allowed is False
    assert decision.freeze is True
    assert "IDEMPOTENCY" in decision.reason


def test_retry_allows_same_key():
    guard = build_guard()

    decision = guard.validate_retry(
        original_key="abc",
        retry_key="abc",
    )

    assert decision.allowed is True
    assert decision.freeze is False


# ---------------------------------------------------------
# RECONCILIATION VALIDATION
# ---------------------------------------------------------

def test_reconciliation_freezes_on_mismatch():
    guard = build_guard()

    decision = guard.validate_reconciliation(
        internal_position=100,
        broker_position=120,
    )

    assert decision.allowed is False
    assert decision.freeze is True
    assert "RECONCILIATION" in decision.reason


def test_reconciliation_allows_match():
    guard = build_guard()

    decision = guard.validate_reconciliation(
        internal_position=100,
        broker_position=100,
    )

    assert decision.allowed is True
    assert decision.freeze is False