# File: tests/screening/test_screening_engine.py
import datetime as dt

from qaai_system.data.ohlcv_store import OHLCVStore
from qaai_system.data.feature_store import FeatureStore
from qaai_system.context.live_context import LiveContext
from screening.engine import ScreeningEngine, ScreenConfig
from screening.results import ScreeningResult
from infra.time_utils import IST


def _ist(ts: dt.datetime) -> dt.datetime:
    if ts.tzinfo is None:
        return ts.replace(tzinfo=IST)
    return ts.astimezone(IST)


def _make_context_with_features():
    ohlcv = OHLCVStore(ignore_off_session=False)
    fs = FeatureStore()

    # basic watchlist
    watchlists = {"DAY_SCALP": ["NIFTY", "BANKNIFTY", "FINNIFTY"]}

    ctx = LiveContext(
        ohlcv_store=ohlcv,
        feature_store=fs,
        watchlists=watchlists,
    )

    # Seed simple OHLCV so last_price etc. would work if needed
    base = _ist(dt.datetime(2025, 1, 1, 9, 15, 0))
    ohlcv.add_tick("NIFTY", 100.0, 10, base)
    ohlcv.add_tick("NIFTY", 102.0, 5, base + dt.timedelta(seconds=10))

    ohlcv.add_tick("BANKNIFTY", 200.0, 10, base)
    ohlcv.add_tick("BANKNIFTY", 198.0, 5, base + dt.timedelta(seconds=10))

    ohlcv.add_tick("FINNIFTY", 150.0, 5, base)
    ohlcv.add_tick("FINNIFTY", 150.3, 5, base + dt.timedelta(seconds=10))

    # Feature snapshots: we supply open/close so engine can compute momentum score
    fs.save_features("NIFTY", "1m", {"open": 100.0, "close": 102.0})
    fs.save_features("BANKNIFTY", "1m", {"open": 200.0, "close": 198.0})
    fs.save_features("FINNIFTY", "1m", {"open": 150.0, "close": 150.3})

    return ctx


def test_screening_engine_ranks_candidates_and_respects_limits():
    ctx = _make_context_with_features()

    cfg = ScreenConfig(
        name="TEST_SCREEN",
        timeframe="1m",
        top_n=2,          # only top-2 by |score|
        min_liquidity=0,  # no liquidity filter here
        watchlist_name="DAY_SCALP",
        prefer_feature_score=False,  # force momentum-based scoring
    )

    engine = ScreeningEngine()
    results = engine.run(ctx, cfg)

    assert len(results) == 2  # capped to top_n

    # type + shape
    assert all(isinstance(r, ScreeningResult) for r in results)

    # NIFTY should be highest positive score; BANKNIFTY negative
    syms = [r.symbol for r in results]
    assert "NIFTY" in syms
    assert any(r.score < 0 for r in results)  # BANKNIFTY bearish

    # sorted by descending |score|
    abs_scores = [abs(r.score) for r in results]
    assert abs_scores == sorted(abs_scores, reverse=True)
