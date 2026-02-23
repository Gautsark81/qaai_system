# 📁 signal_engine/regime_classifier.py — FINAL VERSION WITH MASTER UPGRADE OBJECTIVES

import pandas as pd

# ✅ MASTER UPGRADE OBJECTIVES:
# - Adaptive regime tagging (momentum, mean reversion, volatility burst, choppy)
# - Overlay support for dashboards & report exports


def regime_flags(price_df, window=20):
    if price_df.empty:
        return pd.DataFrame()

    df = price_df.copy()
    df = df.sort_values("timestamp")
    df["returns"] = df["close"].pct_change()
    df["volatility"] = df["returns"].rolling(window).std()
    df["momentum"] = df["close"] - df["close"].rolling(window).mean()

    def classify(row):
        if row["volatility"] > 0.02:
            return "Volatility Burst"
        elif row["momentum"] > 0:
            return "Momentum Up"
        elif row["momentum"] < 0:
            return "Mean Reversion"
        else:
            return "Sideways"

    df["regime"] = df.apply(classify, axis=1)
    return df[["timestamp", "symbol", "close", "volatility", "momentum", "regime"]]
