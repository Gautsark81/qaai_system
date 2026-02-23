from core.execution.execution_mode import ExecutionMode
from core.execution.execute import execute_signal


def test_paper_trading_mutates_virtual_capital_ledger():
    """
    Paper Trading must mutate virtual capital ledger,
    never real capital.
    """

    signal = {
        "symbol": "RELIANCE",
        "side": "BUY",
        "quantity": 10,
        "strategy_id": "paper_capital_test",
    }

    result = execute_signal(
        signal=signal,
        mode=ExecutionMode.PAPER,
    )

    ledger = result.capital_ledger_entry

    assert ledger.strategy_id == "paper_capital_test"
    assert ledger.delta_capital != 0
    assert ledger.is_virtual is True
