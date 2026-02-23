# tests/execution/test_execution_guard_integration.py

import pytest

from core.execution.runtime_capital_guard import RuntimeCapitalGuard


class DummyEnvelope:
    def __init__(self, global_cap, strategy_cap, symbol_cap):
        self.global_cap = global_cap
        self.strategy_cap = strategy_cap
        self.symbol_cap = symbol_cap


class DummyExposure:
    def __init__(self, global_exposure, strategy_exposure, symbol_exposure):
        self.global_exposure = global_exposure
        self.strategy_exposure = strategy_exposure
        self.symbol_exposure = symbol_exposure


class DummyKillSwitch:
    def __init__(self, triggered=False):
        self._triggered = triggered

    def is_triggered(self):
        return self._triggered


class DummyExecutionLoop:
    """
    Minimal simulation of execution loop
    to prove guard authority.
    """

    def __init__(self):
        self.guard = RuntimeCapitalGuard()
        self.frozen = False

    def execute_order(
        self,
        envelope,
        exposure,
        order_value,
        kill_switch=None,
    ):
        decision = self.guard.validate_pre_execution(
            envelope=envelope,
            exposure=exposure,
            proposed_order_value=order_value,
            kill_switch=kill_switch,
        )

        if decision.freeze:
            self.frozen = True
            return decision

        # Simulate fill
        exposure.global_exposure += order_value
        exposure.strategy_exposure += order_value
        exposure.symbol_exposure += order_value

        post = self.guard.validate_post_fill(
            envelope=envelope,
            updated_exposure=exposure,
        )

        if post.freeze:
            self.frozen = True

        return post


# ------------------------------------------------------------
# INTEGRATION TESTS
# ------------------------------------------------------------

def test_execution_loop_allows_valid_trade():
    loop = DummyExecutionLoop()

    envelope = DummyEnvelope(100000, 50000, 20000)
    exposure = DummyExposure(10000, 5000, 2000)

    result = loop.execute_order(
        envelope=envelope,
        exposure=exposure,
        order_value=5000,
    )

    assert result.allowed is True
    assert loop.frozen is False


def test_execution_loop_freezes_on_pre_execution_breach():
    loop = DummyExecutionLoop()

    envelope = DummyEnvelope(15000, 50000, 20000)
    exposure = DummyExposure(12000, 5000, 2000)

    result = loop.execute_order(
        envelope=envelope,
        exposure=exposure,
        order_value=5000,
    )

    assert result.freeze is True
    assert loop.frozen is True


def test_execution_loop_freezes_on_post_fill_drift():
    loop = DummyExecutionLoop()

    envelope = DummyEnvelope(20000, 50000, 20000)
    exposure = DummyExposure(15000, 5000, 2000)

    result = loop.execute_order(
        envelope=envelope,
        exposure=exposure,
        order_value=6000,
    )

    assert result.freeze is True
    assert loop.frozen is True


def test_execution_loop_blocks_on_kill_switch():
    loop = DummyExecutionLoop()

    envelope = DummyEnvelope(100000, 50000, 20000)
    exposure = DummyExposure(10000, 5000, 2000)
    kill_switch = DummyKillSwitch(triggered=True)

    result = loop.execute_order(
        envelope=envelope,
        exposure=exposure,
        order_value=5000,
        kill_switch=kill_switch,
    )

    assert result.freeze is True
    assert loop.frozen is True