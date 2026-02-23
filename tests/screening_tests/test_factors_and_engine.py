from datetime import datetime, timedelta

from infra.time_utils import IST
from data.ohlcv_store import OHLCVStore
from data.feature_store import FeatureStore
from screening.context import ScreeningContext
from screening.factors import compute_intraday_factors, score_factors_linear
from screening.engine import ScreeningEngine, ScreenConfig


def _ist(dt: datetime) -> datetime:
    if dt.tzinfo is None:
        return dt.replace(tzinfo=IST)
    return dt.astimezone(IST)


def test_compute_intraday_factors_basic():
    ohlcv = OHLCVStore(timeframes={"1m": 60})
    features = FeatureStore()
    # TickStore not needed directly here
    class DummyTickStore:
        pass

    ts = _ist(datetime(2025, 1, 1, 9, 31, 0))

    # Create some ticks for NIFTY inside a single 1m bucket
    ohlcv.add_tick("NIFTY", price=100.0, volume=10.0, ts_ist=ts)
    ohlcv.add_tick("NIFTY", price=101.0, volume=5.0, ts_ist=ts + timedelta(seconds=10))
    ohlcv.add_tick("NIFTY", price=99.5, volume=2.0, ts_ist=ts + timedelta(seconds=20))

    ctx = ScreeningContext.from_universe(
        tick_store=DummyTickStore(),
        ohlcv_store=ohlcv,
        feature_store=features,
        as_of=ts,
        universe=["NIFTY"],
        timeframe="1m",
    )

    factors = compute_intraday_factors(ctx, "NIFTY")
    assert "mom_close" in factors
    assert "range" in factors
    assert "liquidity" in factors

    # basic sanity
    assert factors["liquidity"] > 0.0
    assert factors["range"] >= 0.0

    score = score_factors_linear(factors)
    # score might be positive or negative but should be finite
    assert isinstance(score, float)


def test_screening_engine_ranks_by_liquidity_when_momentum_equal():
    ohlcv = OHLCVStore(timeframes={"1m": 60})
    features = FeatureStore()

    class DummyTickStore:
        pass

    base = _ist(datetime(2025, 1, 1, 9, 31, 0))

    # Same close price for both, but very different volume
    # NIFTY: high volume
    ohlcv.add_tick("NIFTY", price=100.0, volume=1000.0, ts_ist=base)
    # BANKNIFTY: low volume
    ohlcv.add_tick("BANKNIFTY", price=100.0, volume=10.0, ts_ist=base)

    ctx = ScreeningContext.from_universe(
        tick_store=DummyTickStore(),
        ohlcv_store=ohlcv,
        feature_store=features,
        as_of=base,
        universe=["NIFTY", "BANKNIFTY"],
        timeframe="1m",
    )

    engine = ScreeningEngine()
    cfg = ScreenConfig(
        name="TEST_LIQ",
        timeframe="1m",
        top_n=10,
        min_liquidity=0.0,
    )

    results = engine.run_screen(ctx, cfg)
    # both symbols should be present
    symbols = [r.symbol for r in results]
    assert set(symbols) == {"NIFTY", "BANKNIFTY"}

    # NIFTY should have the higher score because of higher liquidity
    assert results[0].symbol == "NIFTY"


def test_screening_engine_min_liquidity_filter():
    ohlcv = OHLCVStore(timeframes={"1m": 60})
    features = FeatureStore()

    class DummyTickStore:
        pass

    base = _ist(datetime(2025, 1, 1, 9, 31, 0))

    # NIFTY: decent volume
    ohlcv.add_tick("NIFTY", price=100.0, volume=100.0, ts_ist=base)
    # ILLIQ: zero volume (e.g. bad tick)
    ohlcv.add_tick("ILLIQ", price=100.0, volume=0.0, ts_ist=base)

    ctx = ScreeningContext.from_universe(
        tick_store=DummyTickStore(),
        ohlcv_store=ohlcv,
        feature_store=features,
        as_of=base,
        universe=["NIFTY", "ILLIQ"],
        timeframe="1m",
    )

    engine = ScreeningEngine()
    cfg = ScreenConfig(
        name="TEST_FILTER",
        timeframe="1m",
        top_n=10,
        min_liquidity=1.0,  # filter out effectively illiquid names
    )

    results = engine.run_screen(ctx, cfg)
    symbols = [r.symbol for r in results]
    assert symbols == ["NIFTY"]
