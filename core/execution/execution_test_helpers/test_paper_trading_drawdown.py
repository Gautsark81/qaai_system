from core.execution.execution_mode import ExecutionMode
from core.execution.execute import execute_signal


def test_paper_trading_flags_drawdown_breach():
    """
    Paper Trading must flag drawdown breaches
    without blocking execution.
    """

    signal = {
        "symbol": "RELIANCE",
        "side": "BUY",
        "quantity": 10,
        "strategy_id": "paper_drawdown_test",
    }

    result = execute_signal(
        signal=signal,
        mode=ExecutionMode.PAPER,
    )

    # Deterministic net_unrealized_pnl = 35
    # Max drawdown threshold = -30
    assert result.drawdown_breached is True
    assert result.drawdown_threshold == -30.0
