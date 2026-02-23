import pytest

from modules.strategy_health.state_machine import (
    StrategyStateMachine,
    StrategyState,
    StateMemory,
)
from modules.strategy_health.evaluator import HealthResult


def _health(
    *,
    health_score: float,
    win_rate_score: float,
    flags=None,
):
    """
    Helper to construct HealthResult for tests.
    win_rate_score meanings:
      1.0  -> win rate >= 80%
      0.6  -> 70–79%
      0.4  -> 60–69%
      0.0  -> <60%
    """
    return HealthResult(
        strategy_id="s1",
        health_score=health_score,
        signals={
            "win_rate": win_rate_score,
            "expectancy": 0.6,
            "drawdown": 0.8,
            "consistency": 0.7,
            "activity": 0.8,
        },
        flags=flags or [],
        window=50,
        reason="test",
    )


# ------------------------------------------------------------
# HARD OVERRIDES
# ------------------------------------------------------------

def test_invalid_win_rate_immediately_pauses():
    sm = StrategyStateMachine()
    mem = StateMemory()

    hr = _health(
        health_score=0.9,
        win_rate_score=0.0,
        flags=["WIN_RATE_INVALID"],
    )

    tr = sm.step(
        current_state=StrategyState.ACTIVE,
        health_result=hr,
        memory=mem,
    )

    assert tr is not None
    assert tr.to_state == StrategyState.PAUSED


def test_drawdown_risk_immediately_pauses():
    sm = StrategyStateMachine()
    mem = StateMemory()

    hr = _health(
        health_score=0.8,
        win_rate_score=1.0,
        flags=["DRAWDOWN_RISK"],
    )

    tr = sm.step(
        current_state=StrategyState.ACTIVE,
        health_result=hr,
        memory=mem,
    )

    assert tr is not None
    assert tr.to_state == StrategyState.PAUSED


def test_health_below_critical_immediately_pauses():
    sm = StrategyStateMachine()
    mem = StateMemory()

    hr = _health(
        health_score=0.35,
        win_rate_score=1.0,
    )

    tr = sm.step(
        current_state=StrategyState.WARNING,
        health_result=hr,
        memory=mem,
    )

    assert tr is not None
    assert tr.to_state == StrategyState.PAUSED


# ------------------------------------------------------------
# INSUFFICIENT TRADES
# ------------------------------------------------------------

def test_insufficient_trades_blocks_transition():
    sm = StrategyStateMachine()
    mem = StateMemory()

    hr = _health(
        health_score=0.3,
        win_rate_score=0.0,
        flags=["INSUFFICIENT_TRADES"],
    )

    tr = sm.step(
        current_state=StrategyState.ACTIVE,
        health_result=hr,
        memory=mem,
    )

    assert tr is None


# ------------------------------------------------------------
# SOFT DECAY (PERSISTENCE)
# ------------------------------------------------------------

def test_active_to_warning_requires_two_evaluations():
    sm = StrategyStateMachine()
    mem = StateMemory()

    hr = _health(
        health_score=0.8,
        win_rate_score=0.6,  # <80%
    )

    tr1 = sm.step(
        current_state=StrategyState.ACTIVE,
        health_result=hr,
        memory=mem,
    )
    assert tr1 is None

    tr2 = sm.step(
        current_state=StrategyState.ACTIVE,
        health_result=hr,
        memory=mem,
    )
    assert tr2 is not None
    assert tr2.to_state == StrategyState.WARNING


def test_warning_to_degraded_requires_persistence():
    sm = StrategyStateMachine()
    mem = StateMemory()

    hr = _health(
        health_score=0.6,
        win_rate_score=0.4,  # <70%
    )

    tr1 = sm.step(
        current_state=StrategyState.WARNING,
        health_result=hr,
        memory=mem,
    )
    assert tr1 is None

    tr2 = sm.step(
        current_state=StrategyState.WARNING,
        health_result=hr,
        memory=mem,
    )
    assert tr2 is not None
    assert tr2.to_state == StrategyState.DEGRADED


def test_degraded_to_paused_on_low_health():
    sm = StrategyStateMachine()
    mem = StateMemory()

    hr = _health(
        health_score=0.50,
        win_rate_score=0.6,
    )

    tr = sm.step(
        current_state=StrategyState.DEGRADED,
        health_result=hr,
        memory=mem,
    )

    assert tr is not None
    assert tr.to_state == StrategyState.PAUSED


# ------------------------------------------------------------
# RECOVERY PATH
# ------------------------------------------------------------

def test_degraded_recovers_after_three_clean_evaluations():
    sm = StrategyStateMachine()
    mem = StateMemory()

    hr = _health(
        health_score=0.85,
        win_rate_score=1.0,  # >=80%
    )

    for _ in range(2):
        tr = sm.step(
            current_state=StrategyState.DEGRADED,
            health_result=hr,
            memory=mem,
        )
        assert tr is None

    tr_final = sm.step(
        current_state=StrategyState.DEGRADED,
        health_result=hr,
        memory=mem,
    )

    assert tr_final is not None
    assert tr_final.to_state == StrategyState.ACTIVE
