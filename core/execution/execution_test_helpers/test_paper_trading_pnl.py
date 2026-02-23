from core.execution.execution_mode import ExecutionMode
from core.execution.execute import execute_signal


def test_paper_trading_computes_unrealized_pnl():
    """
    Paper Trading must compute unrealized PnL
    based on virtual fill price.
    """

    signal = {
        "symbol": "RELIANCE",
        "side": "BUY",
        "quantity": 10,
        "strategy_id": "paper_pnl_test",
    }

    result = execute_signal(
        signal=signal,
        mode=ExecutionMode.PAPER,
    )

    # Deterministic placeholder:
    # fill_price = 100.0
    # current_price = 105.0
    # pnl = (105 - 100) * 10 = 50
    assert result.unrealized_pnl == 50.0
