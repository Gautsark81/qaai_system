from core.execution.execution_mode import ExecutionMode
from core.execution.execution_intent import ExecutionIntent
from core.execution.execute import execute_signal


def test_shadow_live_emits_execution_intent_without_side_effects():
    """
    Shadow Live must:
    - Emit ExecutionIntent
    - Perform no execution side effects
    """

    # --------------------------------------------------
    # Arrange
    # --------------------------------------------------

    signal = {
        "symbol": "RELIANCE",
        "side": "BUY",
        "quantity": 10,
        "strategy_id": "strat-shadow-1",
    }

    # --------------------------------------------------
    # Act
    # --------------------------------------------------

    intent = execute_signal(
        signal=signal,
        mode=ExecutionMode.SHADOW,
    )

    # --------------------------------------------------
    # Assert
    # --------------------------------------------------

    assert isinstance(intent, ExecutionIntent)

    assert intent.symbol == "RELIANCE"
    assert intent.side == "BUY"
    assert intent.quantity == 10
    assert intent.strategy_id == "strat-shadow-1"

    assert intent.metadata == {
        "mode": "shadow",
        "shadow": True,
    }
