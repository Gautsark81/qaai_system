# modules/backtest/backtester.py

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from .noise_models import NoiseModels  # ✅ RELATIVE IMPORT (CRITICAL)


class Backtester:
    def __init__(self, initial_capital=100000):
        self.initial_capital = initial_capital

    def run(self, symbol: str, ohlcv: pd.DataFrame, signals: pd.DataFrame):
        capital = self.initial_capital
        position = 0
        entry_price = 0
        trades = []
        equity_curve = []

        for _, row in signals.iterrows():
            timestamp = row["timestamp"]
            signal = row["signal"]
            price = ohlcv.loc[timestamp]["close"] if timestamp in ohlcv.index else None

            if price is None:
                continue

            if signal == "BUY" and position == 0:
                position = capital / price
                entry_price = price
                capital = 0
                trades.append(
                    {
                        "timestamp": timestamp,
                        "symbol": symbol,
                        "action": "BUY",
                        "price": price,
                        "qty": round(position, 4),
                        "pnl": 0.0,
                    }
                )

            elif signal == "SELL" and position > 0:
                pnl = (price - entry_price) * position
                capital = position * price
                trades.append(
                    {
                        "timestamp": timestamp,
                        "symbol": symbol,
                        "action": "SELL",
                        "price": price,
                        "qty": round(position, 4),
                        "pnl": round(float(pnl), 2),
                    }
                )
                position = 0
                entry_price = 0

            equity = capital + position * price if position > 0 else capital
            equity_curve.append(equity)

        if position > 0:
            final_price = ohlcv.iloc[-1]["close"]
            pnl = (final_price - entry_price) * position
            capital = position * final_price
            trades.append(
                {
                    "timestamp": ohlcv.index[-1],
                    "symbol": symbol,
                    "action": "SELL",
                    "price": final_price,
                    "qty": round(position, 4),
                    "pnl": round(float(pnl), 2),
                }
            )
            equity_curve.append(capital)

        total_return = ((capital - self.initial_capital) / self.initial_capital) * 100

        num_closed_trades = sum(1 for t in trades if t["action"] == "SELL")
        wins = sum(1 for t in trades if t["action"] == "SELL" and t["pnl"] > 0)
        win_rate = wins / num_closed_trades if num_closed_trades else 0.0

        returns = [t["pnl"] for t in trades if t["action"] == "SELL"]
        if len(returns) > 1:
            returns = np.array(returns)
            daily_returns = np.diff(returns) / (returns[:-1] + 1e-8)
            sharpe_ratio = (
                np.mean(daily_returns) / (np.std(daily_returns) + 1e-8) * np.sqrt(252)
            )
        else:
            sharpe_ratio = 0.0

        equity_array = np.array(equity_curve)
        if len(equity_array) > 1:
            drawdowns = np.maximum.accumulate(equity_array) - equity_array
            max_drawdown = float(np.max(drawdowns))
        else:
            max_drawdown = 0.0

        metrics = {
            "final_equity": round(float(capital), 2),
            "total_return": round(float(total_return), 2),
            "num_trades": len(trades),
            "win_rate": round(win_rate, 3),
            "sharpe_ratio": round(float(sharpe_ratio), 3),
            "max_drawdown": round(float(max_drawdown), 2),
        }

        return trades, metrics

    def plot_equity_curve(self, equity_curve: list, symbol: str):
        if not equity_curve:
            print("No equity data to plot.")
            return

        plt.figure(figsize=(10, 4))
        plt.plot(equity_curve, marker="o")
        plt.title(f"Equity Curve for {symbol}")
        plt.xlabel("Trade Index")
        plt.ylabel("Equity")
        plt.grid(True)
        plt.tight_layout()
        plt.show()


__all__ = ["Backtester", "NoiseModels"]
