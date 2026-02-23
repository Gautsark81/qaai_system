from core.v2.paper_capital.lifecycle import (
    StrategyLifecycle,
    LifecycleState,
)


def test_lifecycle_progression_to_active():
    lc = StrategyLifecycle(strategy_id="s1")

    lc.record_outcomes([True, True, False])

    assert lc.state == LifecycleState.PAPER_ACTIVE
    assert lc.pnl_history[-1].pnl == 1


def test_lifecycle_decay_and_retire():
    lc = StrategyLifecycle(strategy_id="s2")

    # force losses
    lc.record_outcomes([False, False, False])
    assert lc.state == LifecycleState.DECAYING

    lc.record_outcomes([False, False, False])
    assert lc.state == LifecycleState.RETIRED


def test_lifecycle_recovery_to_active():
    lc = StrategyLifecycle(strategy_id="s3")

    lc.record_outcomes([False, False, False])
    assert lc.state == LifecycleState.DECAYING

    lc.record_outcomes([True, True, True, True])
    assert lc.state == LifecycleState.PAPER_ACTIVE
