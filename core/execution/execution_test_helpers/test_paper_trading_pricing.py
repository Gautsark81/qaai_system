from core.execution.execution_mode import ExecutionMode
from core.execution.execute import execute_signal


def test_paper_trading_attaches_virtual_fill_price():
    """
    Paper Trading must attach a virtual fill price
    to the execution result.
    """

    signal = {
        "symbol": "RELIANCE",
        "side": "BUY",
        "quantity": 10,
        "strategy_id": "paper_price_test",
    }

    result = execute_signal(
        signal=signal,
        mode=ExecutionMode.PAPER,
    )

    assert result.fill_price > 0
    assert result.price_source == "virtual"
