# tests/execution/test_execution_survival_scenarios.py

import pytest
from threading import Thread
from core.execution.runtime_capital_guard import RuntimeCapitalGuard


class Envelope:
    def __init__(self, global_cap, strategy_cap, symbol_cap):
        self.global_cap = global_cap
        self.strategy_cap = strategy_cap
        self.symbol_cap = symbol_cap


class Exposure:
    def __init__(self, global_exposure, strategy_exposure, symbol_exposure):
        self.global_exposure = global_exposure
        self.strategy_exposure = strategy_exposure
        self.symbol_exposure = symbol_exposure


class KillSwitch:
    def __init__(self):
        self.triggered = False

    def is_triggered(self):
        return self.triggered

    def trigger(self):
        self.triggered = True


# ------------------------------------------------------------
# 1️⃣ Partial Fill Followed by Retry
# ------------------------------------------------------------

def test_partial_fill_then_retry_freezes_on_envelope_breach():
    guard = RuntimeCapitalGuard()

    envelope = Envelope(20000, 20000, 20000)
    exposure = Exposure(15000, 15000, 15000)

    # Partial fill of 3000
    exposure.global_exposure += 3000
    exposure.strategy_exposure += 3000
    exposure.symbol_exposure += 3000

    # Retry remaining 3000
    decision = guard.validate_pre_execution(
        envelope=envelope,
        exposure=exposure,
        proposed_order_value=3000,
        kill_switch=None,
    )

    assert decision.freeze is True


# ------------------------------------------------------------
# 2️⃣ Envelope Breach Mid-Loop
# ------------------------------------------------------------

def test_mid_loop_envelope_breach_detected():
    guard = RuntimeCapitalGuard()

    envelope = Envelope(30000, 30000, 30000)
    exposure = Exposure(25000, 25000, 25000)

    # Pre-check passes for small order
    decision = guard.validate_pre_execution(
        envelope=envelope,
        exposure=exposure,
        proposed_order_value=4000,
        kill_switch=None,
    )

    assert decision.allowed is True

    # External drift (market move / other strategy)
    exposure.global_exposure = 31000

    post = guard.validate_post_fill(
        envelope=envelope,
        updated_exposure=exposure,
    )

    assert post.freeze is True


# ------------------------------------------------------------
# 3️⃣ Correlated Exposure Overflow
# ------------------------------------------------------------

def test_correlated_exposure_overflow():
    guard = RuntimeCapitalGuard()

    envelope = Envelope(50000, 50000, 50000)
    exposure = Exposure(48000, 20000, 10000)

    # Order would push global beyond correlated cluster cap
    decision = guard.validate_pre_execution(
        envelope=envelope,
        exposure=exposure,
        proposed_order_value=3000,
        kill_switch=None,
    )

    assert decision.freeze is True


# ------------------------------------------------------------
# 4️⃣ Kill Switch Mid-Execution
# ------------------------------------------------------------

def test_kill_switch_mid_execution():
    guard = RuntimeCapitalGuard()
    ks = KillSwitch()

    envelope = Envelope(100000, 100000, 100000)
    exposure = Exposure(10000, 10000, 10000)

    decision = guard.validate_pre_execution(
        envelope=envelope,
        exposure=exposure,
        proposed_order_value=5000,
        kill_switch=ks,
    )

    assert decision.allowed is True

    # Kill switch triggers mid-execution
    ks.trigger()

    decision2 = guard.validate_pre_execution(
        envelope=envelope,
        exposure=exposure,
        proposed_order_value=1000,
        kill_switch=ks,
    )

    assert decision2.freeze is True


# ------------------------------------------------------------
# 5️⃣ Broker Mismatch Scenario
# ------------------------------------------------------------

def test_broker_reconciliation_mismatch():
    guard = RuntimeCapitalGuard()

    decision = guard.validate_reconciliation(
        internal_position=100,
        broker_position=120,
    )

    assert decision.freeze is True


# ------------------------------------------------------------
# 6️⃣ Concurrent Strategy Execution
# ------------------------------------------------------------

def test_concurrent_strategy_execution_respects_global_cap():
    guard = RuntimeCapitalGuard()

    envelope = Envelope(20000, 20000, 20000)
    exposure = Exposure(10000, 10000, 10000)

    results = []

    def place_order(value):
        decision = guard.validate_pre_execution(
            envelope=envelope,
            exposure=exposure,
            proposed_order_value=value,
            kill_switch=None,
        )
        results.append(decision.freeze)

    t1 = Thread(target=place_order, args=(7000,))
    t2 = Thread(target=place_order, args=(7000,))

    t1.start()
    t2.start()
    t1.join()
    t2.join()

    # At least one must freeze due to global cap constraint
    assert any(results)