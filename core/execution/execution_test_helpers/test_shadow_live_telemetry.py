from core.execution.execution_mode import ExecutionMode
from core.execution.execute import execute_signal


def test_shadow_live_emits_execution_telemetry():
    """
    Shadow Live must emit execution telemetry
    alongside the execution intent.
    """

    signal = {
        "symbol": "RELIANCE",
        "side": "BUY",
        "quantity": 10,
        "strategy_id": "strat-shadow-1",
    }

    intent, telemetry = execute_signal(
        signal=signal,
        mode=ExecutionMode.SHADOW,
        emit_telemetry=True,
    )

    # Intent still correct
    assert intent.symbol == "RELIANCE"
    assert intent.quantity == 10

    # Telemetry invariants
    assert telemetry.mode == "shadow"
    assert telemetry.symbol == "RELIANCE"
    assert telemetry.side == "BUY"
    assert telemetry.quantity == 10
    assert telemetry.strategy_id == "strat-shadow-1"
    assert telemetry.intent == intent
