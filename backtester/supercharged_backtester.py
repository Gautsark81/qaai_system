import pandas as pd


class SuperchargedBacktester:
    def __init__(self):
        self.ticks = []

    def ingest_ticks(self, ticks):
        self.ticks.extend(ticks)

    @staticmethod
    def sma(series: pd.Series, window: int):
        return series.rolling(window).mean()

    def run_strategy(self, strategy_fn, timeframe_seconds: int):
        """
        Fully deterministic.
        No groupby.apply.
        No FutureWarnings.
        Pandas-stable implementation.
        """

        if not self.ticks:
            return {}

        df = pd.DataFrame(self.ticks)

        if "symbol" not in df.columns:
            df["symbol"] = "UNKNOWN"

        if "timestamp" not in df.columns:
            raise ValueError("Ticks must include 'timestamp'")

        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="s")
        df = df.sort_values("timestamp")

        results = {}

        for sym, sym_df in df.groupby("symbol"):
            sym_df = sym_df.set_index("timestamp")

            bars = (
                sym_df.resample(f"{timeframe_seconds}s")
                .agg(
                    close=("price", "last"),
                    volume=("size", "sum"),
                )
                .dropna()
            )

            results[sym] = strategy_fn(sym, bars)

        return results