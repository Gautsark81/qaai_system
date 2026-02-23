from core.execution.execution_mode import ExecutionMode
from core.execution.execute import execute_signal


def test_paper_trading_allocates_virtual_capital_only():
    """
    Paper Trading must:
    - Execute intent
    - Mutate ONLY virtual capital
    - Never call real broker
    """

    signal = {
        "symbol": "RELIANCE",
        "side": "BUY",
        "quantity": 10,
        "strategy_id": "paper_strat_1",
    }

    result = execute_signal(
        signal=signal,
        mode=ExecutionMode.PAPER,
    )

    # Result must include paper execution info
    assert result.execution_mode == "paper"
    assert result.virtual_fill is True
    assert result.real_broker_called is False
