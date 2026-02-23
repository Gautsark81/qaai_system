# strategies/sma_crossover.py

import pandas as pd


def sma_crossover_strategy(df, short=10, long=20, qty=1):
    """
    Generate trades using SMA crossover.
    Returns list of trade dicts.
    """
    df = df.copy()
    df["sma_short"] = df["close"].rolling(short).mean()
    df["sma_long"] = df["close"].rolling(long).mean()

    trades = []
    position = None

    for i in range(len(df)):
        row = df.iloc[i]
        if pd.isna(row["sma_short"]) or pd.isna(row["sma_long"]):
            continue

        # Buy signal
        if row["sma_short"] > row["sma_long"] and position != "long":
            trades.append(
                {
                    "symbol": "TEST",
                    "side": "BUY",
                    "quantity": qty,
                    "entry_price": row["close"],
                    "exit_price": None,
                    "status": "open",
                    "strategy_id": "sma_crossover",
                    "timestamp": row["date"],
                }
            )
            position = "long"

        # Sell signal
        elif row["sma_short"] < row["sma_long"] and position != "short":
            trades.append(
                {
                    "symbol": "TEST",
                    "side": "SELL",
                    "quantity": qty,
                    "entry_price": row["close"],
                    "exit_price": None,
                    "status": "open",
                    "strategy_id": "sma_crossover",
                    "timestamp": row["date"],
                }
            )
            position = "short"

    return trades
