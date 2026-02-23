from datetime import datetime

from infra.time_utils import IST
from data.tick_store import TickStore
from data.ohlcv_store import OHLCVStore
from data.feature_store import FeatureStore
from screener.jobs import ScreenerJobs
from watchlist.service import WatchlistService


def _ist(dt: datetime) -> datetime:
    if dt.tzinfo is None:
        return dt.replace(tzinfo=IST)
    return dt.astimezone(IST)


def test_screener_jobs_populates_watchlists(tmp_path):
    # Data infra
    tick_store = TickStore(db_path=":memory:", retention_seconds=None)
    ohlcv = OHLCVStore(timeframes={"1m": 60, "5m": 300})
    features = FeatureStore()

    # Watchlist with persistence
    wl = WatchlistService(base_dir=str(tmp_path / "watchlists"))

    # Universe
    universe = ["NIFTY", "BANKNIFTY"]

    jobs = ScreenerJobs(
        tick_store=tick_store,
        ohlcv_store=ohlcv,
        feature_store=features,
        watchlist=wl,
        universe=universe,
    )

    # Seed some basic OHLCV data so the screener has something to work with
    base = _ist(datetime(2025, 1, 1, 9, 31, 0))
    # single ticks are enough for factors to exist
    ohlcv.add_tick("NIFTY", price=100.0, volume=100.0, ts_ist=base)
    ohlcv.add_tick("BANKNIFTY", price=200.0, volume=50.0, ts_ist=base)

    # Run pre-market screen (5m timeframe)
    jobs.run_pre_market_screen()
    day_scalp = wl.get("DAY_SCALP")
    assert len(day_scalp) > 0

    # Run intraday refresh (1m timeframe)
    jobs.run_intraday_refresh()
    intraday_core = wl.get("INTRADAY_CORE")
    assert len(intraday_core) > 0

    # Sanity: symbols should be from universe
    assert set(day_scalp).issubset(set(universe))
    assert set(intraday_core).issubset(set(universe))
