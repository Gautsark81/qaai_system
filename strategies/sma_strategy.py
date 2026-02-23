# qaai_system/strategies/sma_strategy.py
import pandas as pd


class SMAStrategy:
    """
    Simple Moving Average (SMA) Crossover Strategy.
    - Buys when short SMA crosses above long SMA
    - Sells (closes) when short SMA crosses below long SMA
    """

    def __init__(self, short_window=20, long_window=50, qty=1, strategy_id="sma_strategy"):
        self.short = int(short_window)
        self.long = int(long_window)
        self.qty = int(qty)
        self.strategy_id = strategy_id
        self.df = pd.DataFrame()

    def load_data(self, df: pd.DataFrame):
        """
        Load and preprocess OHLCV data.
        Ensures we always have a 'timestamp' column for signals.
        """
        df = df.copy()

        # Normalize date/timestamp
        if "timestamp" not in df.columns:
            if "date" in df.columns:
                df["timestamp"] = pd.to_datetime(df["date"])
            else:
                raise ValueError("Data must contain either 'timestamp' or 'date' column.")

        df["timestamp"] = pd.to_datetime(df["timestamp"])
        df = df.sort_values("timestamp").reset_index(drop=True)

        # Add moving averages
        df["sma_short"] = df["close"].rolling(self.short, min_periods=1).mean()
        df["sma_long"] = df["close"].rolling(self.long, min_periods=1).mean()

        self.df = df

    def generate_signals(self):
        """
        Generate trade signals based on SMA crossover.
        Returns a list of trade dicts compatible with PnLCalculator.
        """
        if self.df.empty:
            return []

        df = self.df.copy()
        trades = []
        position = 0
        entry_price, entry_time = None, None

        for i in range(1, len(df)):
            prev_short = df.loc[i - 1, "sma_short"]
            prev_long = df.loc[i - 1, "sma_long"]
            cur_short = df.loc[i, "sma_short"]
            cur_long = df.loc[i, "sma_long"]

            # Entry condition: short SMA crosses above long SMA
            if position == 0 and prev_short <= prev_long and cur_short > cur_long:
                entry_price = float(df.loc[i, "open"]) if "open" in df.columns else float(df.loc[i, "close"])
                entry_time = df.loc[i, "timestamp"]
                position = 1

            # Exit condition: short SMA crosses below long SMA
            elif position == 1 and prev_short >= prev_long and cur_short < cur_long:
                exit_price = float(df.loc[i, "open"]) if "open" in df.columns else float(df.loc[i, "close"])
                exit_time = df.loc[i, "timestamp"]

            trades.append(
                {
                    "symbol": df.loc[i, "symbol"] if "symbol" in df.columns else None,
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

        # If still holding a position at the end → mark as open trade
        if position == 1 and entry_price is not None:
            trades.append(
                {
                    "symbol": df.iloc[-1].get("symbol", None),
                    "side": "BUY",
                    "quantity": self.qty,
                    "entry_price": entry_price,
                    "exit_price": None,
                    "status": "open",
                    "timestamp": entry_time,
                    "exit_timestamp": None,
                    "strategy_id": self.strategy_id,
                }
            )

        return trades
