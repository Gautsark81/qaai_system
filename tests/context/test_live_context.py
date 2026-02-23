# File: tests/context/test_live_context.py
import datetime as dt

from qaai_system.context.live_context import LiveContext
from qaai_system.data.ohlcv_store import OHLCVStore
from qaai_system.data.feature_store import FeatureStore
from infra.time_utils import IST


def _ist(ts: dt.datetime) -> dt.datetime:
    if ts.tzinfo is None:
        return ts.replace(tzinfo=IST)
    return ts.astimezone(IST)


def test_live_context_watchlist_and_last_price():
    ohlcv = OHLCVStore(ignore_off_session=False)
    features = FeatureStore()
    ctx = LiveContext(
        ohlcv_store=ohlcv,
        feature_store=features,
        watchlists={"DAY_SCALP": ["NIFTY", "BANKNIFTY"]},
    )

    assert ctx.watchlist("DAY_SCALP") == ["NIFTY", "BANKNIFTY"]
    assert ctx.watchlist("UNKNOWN") == []

    base = _ist(dt.datetime(2025, 1, 1, 9, 15, 0))
    ohlcv.add_tick("NIFTY", 100.0, 10, base)
    ohlcv.add_tick("NIFTY", 101.0, 5, base + dt.timedelta(seconds=10))

    last_price = ctx.get_last_price("NIFTY", "1m")
    assert last_price == 101.0


def test_live_context_feature_snapshot_and_vwap_fallback():
    ohlcv = OHLCVStore(ignore_off_session=False)
    features = FeatureStore()
    ctx = LiveContext(ohlcv_store=ohlcv, feature_store=features, watchlists={})

    base = _ist(dt.datetime(2025, 1, 1, 9, 15, 0))
    for i in range(3):
        ohlcv.add_tick("BANKNIFTY", 200.0 + i, 1, base + dt.timedelta(seconds=10 * i))

    # no flat snapshot yet, so uses streaming latest
    features.update("BANKNIFTY", "1m", base.timestamp(), {"ema": 201.0}, regime="trend")

    snap = ctx.get_feature_snapshot("BANKNIFTY", "1m")
    assert snap["ema"] == 201.0
    assert snap["regime"] == "trend"

    vwap = ctx.get_vwap("BANKNIFTY", "1m")
    assert vwap > 0.0
