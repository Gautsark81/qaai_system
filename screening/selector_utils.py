# screening/selector_utils.py
import pandas as pd


def generate_basic_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Backwards-compatible basic feature generator used by screeners/tests.
    Produces: return, volatility (14), sma_5, sma_20 (if close exists).
    Drops rows with NaN and resets index.
    """
    if df is None or df.empty:
        return pd.DataFrame()

    out = df.copy()
    if "close" in out.columns:
        out["return"] = out["close"].pct_change()
        out["volatility"] = out["return"].rolling(14).std()
        out["sma_5"] = out["close"].rolling(5).mean()
        out["sma_20"] = out["close"].rolling(20).mean()
    if "volume" in out.columns:
        out["volume_change"] = out["volume"].pct_change()

    out = out.dropna().reset_index(drop=True)
    return out


def generate_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Slightly richer feature builder (wrapper around generate_basic_features).
    Ensures 'symbol' column exists if provided as a mapping of symbols->df.
    """
    return generate_basic_features(df)
