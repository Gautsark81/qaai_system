# tests/execution/test_phase14_governance_and_safety.py

import pytest

from core.execution.execute import execute_signal
from core.execution.execution_mode import ExecutionMode
from core.execution.governance import (
    ExecutionGovernance,
    ExecutionPromotion,
)
from core.operations.arming import (
    ExecutionArming,
    SystemArmingState,
)
from core.capital.safety import CapitalViolation


BASE_SIGNAL = {
    "symbol": "INFY",
    "side": "BUY",
    "quantity": 10,
    "strategy_id": "STRAT_TEST",
}


def test_shadow_always_allowed_when_governed():
    result = execute_signal(
        signal=BASE_SIGNAL,
        mode=ExecutionMode.SHADOW,
        governance=ExecutionGovernance(
            promotion_level=ExecutionPromotion.SHADOW_ONLY
        ),
        arming=ExecutionArming(
            state=SystemArmingState.DISARMED
        ),
    )

    assert result["status"] == "SHADOW_EXECUTED"


def test_paper_blocked_when_not_armed():
    with pytest.raises(Exception):
        execute_signal(
            signal=BASE_SIGNAL,
            mode=ExecutionMode.PAPER,
            governance=ExecutionGovernance(
                promotion_level=ExecutionPromotion.SHADOW_AND_PAPER
            ),
            arming=ExecutionArming(
                state=SystemArmingState.DISARMED
            ),
        )


def test_paper_blocked_when_capital_exceeded():
    signal = {
        **BASE_SIGNAL,
        "base_price": 1_000_000.0,
        "max_per_trade_exposure": 10_000.0,
    }

    with pytest.raises(CapitalViolation):
        execute_signal(
            signal=signal,
            mode=ExecutionMode.PAPER,
            governance=ExecutionGovernance(
                promotion_level=ExecutionPromotion.SHADOW_AND_PAPER
            ),
            arming=ExecutionArming(
                state=SystemArmingState.ARMED
            ),
        )


def test_live_never_allowed():
    assert not hasattr(ExecutionMode, "LIVE")

