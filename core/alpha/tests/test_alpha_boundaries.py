from core.execution.execution_mode import ExecutionMode
from core.execution.execute import execute_signal
from core.alpha.shadow_diagnostics import analyze_shadow_alpha


def test_alpha_cannot_modify_execution_intent():
    """
    Alpha diagnostics must never modify execution intent.
    This test enforces Shadow Live governance boundaries.
    """

    signal = {
        "symbol": "RELIANCE",
        "side": "BUY",
        "quantity": 10,
        "strategy_id": "boundary-test",
    }

    intent_before = execute_signal(
        signal=signal,
        mode=ExecutionMode.SHADOW,
    )

    _ = analyze_shadow_alpha(
        signal=signal,
        intent=intent_before,
    )

    intent_after = execute_signal(
        signal=signal,
        mode=ExecutionMode.SHADOW,
    )

    assert intent_before == intent_after
