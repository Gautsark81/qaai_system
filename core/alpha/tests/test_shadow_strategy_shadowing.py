from core.execution.execution_mode import ExecutionMode
from core.execution.execute import execute_signal
from core.alpha.shadow_shadowing import run_shadow_strategies


def test_shadow_strategies_run_in_parallel_without_execution_influence():
    """
    Shadow strategies must:
    - Run in parallel
    - Produce hypothetical intents
    - NOT affect primary execution
    """

    signal = {
        "symbol": "RELIANCE",
        "side": "BUY",
        "quantity": 10,
        "strategy_id": "primary_strat",
    }

    # Primary execution (real shadow live)
    primary_intent = execute_signal(
        signal=signal,
        mode=ExecutionMode.SHADOW,
    )

    # Shadow strategies
    shadow_results = run_shadow_strategies(
        signal=signal,
        shadow_strategy_ids=[
            "shadow_strat_A",
            "shadow_strat_B",
        ],
    )

    # Primary intent unchanged
    primary_intent_after = execute_signal(
        signal=signal,
        mode=ExecutionMode.SHADOW,
    )
    assert primary_intent == primary_intent_after

    # Shadow results
    assert len(shadow_results) == 2

    for result in shadow_results:
        assert result.strategy_id in {
            "shadow_strat_A",
            "shadow_strat_B",
        }
        assert result.hypothetical_intent is not None
        assert result.hypothetical_intent != primary_intent
        assert 0.0 <= result.confidence_score <= 1.0
