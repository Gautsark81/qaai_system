from core.execution.execution_mode import ExecutionMode
from core.execution.execute import execute_signal


def test_shadow_live_is_deterministic_for_same_signal():
    """
    Shadow Live replay invariant:
    Same signal + same mode must produce identical ExecutionIntent.
    """

    signal = {
        "symbol": "RELIANCE",
        "side": "BUY",
        "quantity": 10,
        "strategy_id": "strat-shadow-1",
    }

    intent_1 = execute_signal(
        signal=signal,
        mode=ExecutionMode.SHADOW,
    )

    intent_2 = execute_signal(
        signal=signal,
        mode=ExecutionMode.SHADOW,
    )

    assert intent_1 == intent_2
