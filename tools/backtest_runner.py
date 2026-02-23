# tools/backtest_runner.py

import pandas as pd

from backtest.backtester import Backtester


def main():
    # Minimal dummy data just to prove end-to-end works
    ohlcv = pd.DataFrame(
        {
            "close": [100, 102, 101, 103, 105],
        },
        index=pd.date_range("2024-01-01", periods=5),
    )

    signals = pd.DataFrame(
        {
            "timestamp": ohlcv.index,
            "signal": ["BUY", None, None, "SELL", None],
        }
    )

    bt = Backtester(initial_capital=100_000)
    trades, metrics = bt.run("NIFTY", ohlcv, signals)

    print("Trades:", trades)
    print("Metrics:", metrics)


if __name__ == "__main__":
    main()
