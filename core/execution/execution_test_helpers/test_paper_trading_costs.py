from core.execution.execution_mode import ExecutionMode
from core.execution.execute import execute_signal


def test_paper_trading_applies_fees_and_slippage():
    """
    Paper Trading must adjust unrealized PnL
    for deterministic fees and slippage.
    """

    signal = {
        "symbol": "RELIANCE",
        "side": "BUY",
        "quantity": 10,
        "strategy_id": "paper_cost_test",
    }

    result = execute_signal(
        signal=signal,
        mode=ExecutionMode.PAPER,
    )

    # Base PnL = (105 - 100) * 10 = 50
    # Slippage = 1 per unit * 10 = 10
    # Fee = 5
    # Net PnL = 50 - 10 - 5 = 35
    assert result.net_unrealized_pnl == 35.0
