# qaai_system/modules/signal_engine.py

import pandas as pd


class SignalEngineSupercharged:
    """
    Enhanced signal engine with a basic strategy.
    """

    def __init__(self, config=None):
        self.config = config or {}

    def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Generate signals:
        - buy if close > open
        - sell if close < open
        - hold otherwise
        """
        signals = []
        for _, row in df.iterrows():
            if row["close"] > row["open"]:
                signals.append("buy")
            elif row["close"] < row["open"]:
                signals.append("sell")
            else:
                signals.append("hold")

        df_out = df.copy()
        df_out["signal"] = signals
        return df_out


# --- Backwards compatibility ---
SignalEngine = SignalEngineSupercharged
