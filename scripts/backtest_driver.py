# scripts/backtest_driver.py
"""
CLI Backtest Driver
Usage (single symbol):
  python scripts/backtest_driver.py --symbol RELIANCE --start 2023-09-01 --end 2024-09-01 --db sqlite:///qaai.db

Usage (multi-symbol portfolio):
  python scripts/backtest_driver.py --symbols RELIANCE TCS INFY --start 2023-09-01 --end 2024-09-01 --db sqlite:///qaai.db
"""
from __future__ import annotations
import argparse
import os
import sys
import matplotlib.pyplot as plt
import pandas as pd

# Robust imports
try:
    from qaai_system.backtester.backtester import Backtester
except Exception:
    sys.path.insert(0, os.path.abspath(os.path.join(os.getcwd(), "..")))
    from qaai_system.backtester.backtester import Backtester

# Try SMA strategy, else fallback
try:
    from qaai_system.strategies.sma_strategy import SMAStrategy

    SMA_PRESENT = True
except Exception:
    SMA_PRESENT = False

# Noise injector
try:
    from qaai_system.utils import noise_injector

    NOISE_PRESENT = True
except Exception:
    NOISE_PRESENT = False


# ---------------- Fallback SMA strategy ----------------
class FallbackSMAStrategy:
    def __init__(
        self, short_window=20, long_window=50, qty=1, strategy_id="sma_fallback"
    ):
        self.short = int(short_window)
        self.long = int(long_window)
        self.qty = int(qty)
        self.strategy_id = strategy_id
        self.df = pd.DataFrame()

    def load_data(self, df: pd.DataFrame):
        df = df.copy()
        if "timestamp" not in df.columns and "date" in df.columns:
            df["timestamp"] = pd.to_datetime(df["date"])
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        df = df.sort_values("timestamp").reset_index(drop=True)
        self.df = df

    def generate_signals(self):
        if self.df is None or self.df.empty:
            return []
        df = self.df.copy()
        df["sma_short"] = df["close"].rolling(self.short, min_periods=1).mean()
        df["sma_long"] = df["close"].rolling(self.long, min_periods=1).mean()

        position = 0
        entry_price, entry_time = None, None
        trades = []

        for i in range(1, len(df)):
            prev_short, prev_long = (
                df.loc[i - 1, "sma_short"],
                df.loc[i - 1, "sma_long"],
            )
            cur_short, cur_long = df.loc[i, "sma_short"], df.loc[i, "sma_long"]

            # Entry
            if position == 0 and prev_short <= prev_long and cur_short > cur_long:
                entry_price = (
                    float(df.loc[i, "open"])
                    if "open" in df.columns
                    else float(df.loc[i, "close"])
                )
                entry_time = df.loc[i, "timestamp"]
                position = 1
                trades.append(
                    {
                        "symbol": (
                            df.loc[i, "symbol"] if "symbol" in df.columns else None
                        ),
                        "side": "BUY",
                        "quantity": self.qty,
                        "entry_price": entry_price,
                        "exit_price": None,
                        "status": "open",
                        "timestamp": entry_time,
                        "exit_timestamp": None,
                        "strategy_id": self.strategy_id,
                        "reason": f"SMA{self.short} crossed above SMA{self.long} → entry trade",
                    }
                )

            # Exit
            elif position == 1 and prev_short >= prev_long and cur_short < cur_long:
                exit_price = (
                    float(df.loc[i, "open"])
                    if "open" in df.columns
                    else float(df.loc[i, "close"])
                )
                exit_time = df.loc[i, "timestamp"]
                trades.append(
                    {
                        "symbol": (
                            df.loc[i, "symbol"] if "symbol" in df.columns else None
                        ),
                        "side": "BUY",
                        "quantity": self.qty,
                        "entry_price": entry_price,
                        "exit_price": exit_price,
                        "status": "closed",
                        "timestamp": entry_time,
                        "exit_timestamp": exit_time,
                        "strategy_id": self.strategy_id,
                        "reason": f"SMA{self.short} crossed below SMA{self.long} → exit trade",
                    }
                )
                position, entry_price, entry_time = 0, None, None

        # Open at end
        if position == 1 and entry_price is not None:
            trades.append(
                {
                    "symbol": df.iloc[-1]["symbol"] if "symbol" in df.columns else None,
                    "side": "BUY",
                    "quantity": self.qty,
                    "entry_price": entry_price,
                    "exit_price": None,
                    "status": "open",
                    "timestamp": entry_time,
                    "exit_timestamp": None,
                    "strategy_id": self.strategy_id,
                    "reason": f"SMA{self.short} > SMA{self.long} at end of backtest → holding open position",
                }
            )

        return trades


# ---------------- Runner ----------------
def run_backtest(
    bt: Backtester, symbols, start: str, end: str, db_url: str, noise_model: str = None
):
    multi_symbol = isinstance(symbols, (list, tuple)) and len(symbols) > 1
    label = ", ".join(symbols) if multi_symbol else symbols[0]
    print(f"[RUN] Backtest: {label} {start} -> {end} using DB {db_url}")

    # Choose strategy
    if SMA_PRESENT:
        try:
            strat = SMAStrategy(short_window=20, long_window=50, qty=1)
        except Exception:
            strat = FallbackSMAStrategy()
    else:
        strat = FallbackSMAStrategy()

    def strategy_fn(df: pd.DataFrame):
        if noise_model and NOISE_PRESENT:
            df = noise_injector.apply_noise(df, model=noise_model)
            print(f"[INFO] Applied {noise_model} noise to OHLCV data")
        strat.load_data(df)
        return strat.generate_signals()

    # Run single or multi-symbol
    if multi_symbol:
        result = bt.run_portfolio(symbols, start, end, strategy_fn)
    else:
        result = bt.run(symbols[0], start, end, strategy_fn)

    pnl_df, summary, fills = (
        result["pnl_df"],
        result["summary"],
        result.get("fills", []),
    )

    print("\n===== Backtest Summary =====")
    for k, v in summary.items():
        if k not in ("sharpe_ratio", "max_drawdown", "volatility"):
            print(f"{k}: {v}")

    if any(k in summary for k in ["sharpe_ratio", "max_drawdown", "volatility"]):
        print("\n===== Risk Metrics =====")
        if "sharpe_ratio" in summary:
            print(f"Sharpe Ratio: {summary['sharpe_ratio']:.3f}")
        if "max_drawdown" in summary:
            print(f"Max Drawdown: {summary['max_drawdown']:.2f}")
        if "volatility" in summary:
            print(f"Volatility: {summary['volatility']:.3f}")

    # Per-symbol breakdown if multi-symbol
    if multi_symbol and fills:
        print("\n===== Per-Symbol Breakdown =====")
        fills_df = pd.DataFrame(fills)
        if "symbol" in fills_df.columns:
            per_symbol = (
                fills_df.groupby("symbol").size().reset_index(name="num_trades")
            )
            if "exit_price" in fills_df.columns and "price" in fills_df.columns:
                fills_df["realized_pnl"] = fills_df.apply(
                    lambda r: (
                        (r["exit_price"] - r["price"]) * r["qty"]
                        if pd.notnull(r.get("exit_price"))
                        and pd.notnull(r.get("price"))
                        else 0.0
                    ),
                    axis=1,
                )
                pnl_per_symbol = (
                    fills_df.groupby("symbol")["realized_pnl"].sum().reset_index()
                )
                per_symbol = per_symbol.merge(pnl_per_symbol, on="symbol", how="left")
            print(per_symbol.to_string(index=False))

    if fills:
        print("\n===== Executed Trades (Fills) =====")
        fills_df = pd.DataFrame(fills)
        cols_to_show = [
            c
            for c in [
                "symbol",
                "side",
                "qty",
                "price",
                "exit_price",
                "timestamp",
                "strategy_id",
                "reason",
            ]
            if c in fills_df.columns
        ]
        print(fills_df[cols_to_show].head(20).to_string(index=False))
        if len(fills_df) > 20:
            print(f"... ({len(fills_df) - 20} more trades)")
    else:
        print("\n[INFO] No fills recorded.")

    if pnl_df is not None and not pnl_df.empty:
        pnl_df["cumulative_pnl"] = pnl_df["total_pnl"].cumsum()
        x = pnl_df["timestamp"] if "timestamp" in pnl_df.columns else range(len(pnl_df))
        plt.figure(figsize=(10, 4))
        plt.plot(x, pnl_df["cumulative_pnl"], marker="o")
        plt.title(f"Equity Curve ({label})")
        plt.xlabel("Time")
        plt.ylabel("Cumulative PnL")
        plt.grid(True)
        plt.tight_layout()
        plt.show()
    else:
        print("[INFO] No trades / PnL to plot.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Backtest driver")
    parser.add_argument("--symbol", help="Single symbol to backtest")
    parser.add_argument(
        "--symbols", nargs="+", help="List of symbols for portfolio backtest"
    )
    parser.add_argument("--start", required=True)
    parser.add_argument("--end", required=True)
    parser.add_argument("--db", default="sqlite:///qaai.db")
    parser.add_argument(
        "--noise",
        choices=["gaussian", "uniform", "jump"],
        help="Apply noise model to OHLCV data",
    )
    args = parser.parse_args()

    bt = Backtester(db_url=args.db)

    if args.symbols:
        run_backtest(
            bt,
            args.symbols,
            args.start,
            args.end,
            db_url=args.db,
            noise_model=args.noise,
        )
    elif args.symbol:
        run_backtest(
            bt,
            [args.symbol],
            args.start,
            args.end,
            db_url=args.db,
            noise_model=args.noise,
        )
    else:
        print("Error: must provide --symbol or --symbols")
