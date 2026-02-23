# scripts/extract_features.py
"""
Small integration helper:
 - reads ticks from TickStore for provided symbols
 - converts recent ticks into a single 1-min OHLCV (using existing util)
 - builds features and saves to FeatureStore
Usage:
    python -m scripts.extract_features  # runs default demo
"""

import time
from data.tick_store import TickStore
from data.ohlcv import ticks_to_1min_ohlcv
from data.feature_store import FeatureStore
from data.indicators import build_features_from_ohlcv


def extract_for_symbol(
    ts: TickStore, fs: FeatureStore, symbol: str, timeframe: str = "1m"
):
    """
    Read ticks for symbol (last retention window), compute OHLCV (single bucket),
    then compute features and save to FeatureStore.
    """
    ticks = ts.get_ticks(symbol, since=0)
    if not ticks:
        return False
    ohlcv = [ticks_to_1min_ohlcv(ticks)]  # single-bucket list
    # If conversion failed, skip
    if not ohlcv or not ohlcv[0]:
        return False
    features = build_features_from_ohlcv(ohlcv)
    fs.save_features(symbol, timeframe, features)
    return True


def run_demo():
    ts = TickStore()
    fs = FeatureStore()
    # demo: create a few ticks for symbol TST
    now = time.time()
    ticks = [
        {"timestamp": now, "price": 100.0, "size": 1},
        {"timestamp": now, "price": 101.0, "size": 2},
        {"timestamp": now, "price": 99.5, "size": 1},
    ]
    for t in ticks:
        ts.append_tick("TST", t)
    ok = extract_for_symbol(ts, fs, "TST")
    print("Extracted features for TST:", ok)
    if ok:
        print("Saved snapshot:", fs.snapshot())


if __name__ == "__main__":
    run_demo()
