# scripts/run_paper_test.py

from core.execution.execute import execute_signal
from core.execution.execution_mode import ExecutionMode


def main():
    signal = {
        "symbol": "INFY",
        "side": "BUY",
        "quantity": 10,
        "strategy_id": "STRAT_PAPER_TEST",
        # Optional deterministic inputs
        "base_price": 1500.0,
        "slippage_per_unit": 0.5,
        "flat_fee": 5.0,
    }

    result = execute_signal(
        signal=signal,
        mode=ExecutionMode.PAPER,
    )

    print("\n=== PAPER EXECUTION RESULT ===")
    print(result)
    print("\nLedger delta:", result.ledger_entry.delta_capital)


if __name__ == "__main__":
    main()
