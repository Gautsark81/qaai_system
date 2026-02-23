import pandas as pd


def build_watchlist(
    stock_df: pd.DataFrame,
    top_k: int = 100,
) -> pd.DataFrame:
    """
    Build a ranked watchlist from raw stock feature data.

    Expected by tests:
    - returns a DataFrame
    - has column 'final_score'
    - sorted descending by final_score
    - length == top_k
    """

    if "symbol" not in stock_df.columns:
        raise ValueError("stock_df must contain 'symbol' column")

    # -----------------------------
    # Deterministic scoring model
    # -----------------------------
    # Simple, transparent composite score
    score_components = []

    if "signal_strength" in stock_df.columns:
        score_components.append(stock_df["signal_strength"])

    if "rsi" in stock_df.columns:
        score_components.append(stock_df["rsi"] / 100.0)

    if "ma_ratio" in stock_df.columns:
        score_components.append(stock_df["ma_ratio"] / 2.0)

    if "atr" in stock_df.columns:
        score_components.append(1.0 / (1.0 + stock_df["atr"]))

    if "bbw" in stock_df.columns:
        score_components.append(1.0 / (1.0 + stock_df["bbw"]))

    if not score_components:
        raise ValueError("No usable features to compute final_score")

    # -----------------------------
    # Final score
    # -----------------------------
    final_score = sum(score_components) / len(score_components)

    watchlist = stock_df.copy()
    watchlist["final_score"] = final_score

    # -----------------------------
    # Rank & select top K
    # -----------------------------
    watchlist = watchlist.sort_values(
        by="final_score",
        ascending=False,
    ).head(top_k)

    # Reset index for clean iloc behavior
    return watchlist.reset_index(drop=True)


def filter_for_signal_generation(
    signal_df: pd.DataFrame,
    watchlist_df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Filter signal candidates to only those present in the watchlist.
    """

    if "symbol" not in signal_df.columns:
        raise ValueError("signal_df must contain 'symbol' column")

    if "symbol" not in watchlist_df.columns:
        raise ValueError("watchlist_df must contain 'symbol' column")

    return signal_df[
        signal_df["symbol"].isin(watchlist_df["symbol"])
    ].reset_index(drop=True)
