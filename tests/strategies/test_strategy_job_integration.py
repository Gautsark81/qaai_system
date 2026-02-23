from strategies.base import StrategyBase
from strategies.jobs import StrategyJob
from strategies.momentum_intraday import MomentumIntradayStrategy


# -----------------------
# Fakes
# -----------------------
class FakeWatchlistService:
    def __init__(self, lists):
        # lists: {name: [symbols]}
        self._lists = dict(lists)

    def get(self, name):
        return list(self._lists.get(name, []))


class FakeFeatureStore:
    def __init__(self, data):
        # data: {(symbol, timeframe): features_dict}
        self._data = dict(data)

    def latest(self, symbol, timeframe):
        return self._data.get((symbol, timeframe), {})


class FakeOHLCVStore:
    def __init__(self, data):
        # data: {(symbol, timeframe): bar_dict}
        self._data = dict(data)

    def latest_bar(self, symbol, timeframe):
        return self._data.get((symbol, timeframe))


class FakeRouter:
    def __init__(self):
        self.submitted = []

    def submit(self, plan):
        self.submitted.append(plan)
        # simulate returning some id or dict, but StrategyJob doesn't care
        return {"status": "submitted", "order_id": f"fake_{len(self.submitted)}"}


# -----------------------
# Tests
# -----------------------
def test_strategy_job_runs_strategy_over_watchlist_and_calls_router():
    # Arrange: watchlist with two symbols
    wl = FakeWatchlistService(
        {"DAY_SCALP": ["NIFTY", "BANKNIFTY"]}
    )

    # Bar + features snapshot
    ohlcv = FakeOHLCVStore(
        {
            ("NIFTY", "1m"): {"open": 100.0, "close": 101.0},
            ("BANKNIFTY", "1m"): {"open": 200.0, "close": 199.0},
        }
    )

    fs = FakeFeatureStore(
        {
            ("NIFTY", "1m"): {"screen_score": 1.0, "atr": 1.0},
            ("BANKNIFTY", "1m"): {"screen_score": -0.8, "atr": 2.0},
        }
    )

    router = FakeRouter()

    strategy = MomentumIntradayStrategy(
        config={
            "min_score": 0.0,
            "base_size": 1.0,
            "max_size": 10.0,
            "inv_vol_target": 0.0,  # disable vol scaling for simpler expectations
            "tag": "JOB_TEST",
        }
    )

    job = StrategyJob(
        strategy=strategy,
        router=router,
        watchlists=wl,
        feature_store=fs,
        ohlcv_store=ohlcv,
        config={"watchlist_name": "DAY_SCALP", "timeframe": "1m"},
    )

    # Act
    submitted_orders = job.run_once()

    # Assert: both symbols should result in orders (one BUY, one SELL)
    assert len(submitted_orders) == 2
    assert len(router.submitted) == 2

    syms = {o["symbol"] for o in submitted_orders}
    assert syms == {"NIFTY", "BANKNIFTY"}

    # Check sides
    sides = {o["symbol"]: o["side"] for o in submitted_orders}
    assert sides["NIFTY"] == "BUY"
    assert sides["BANKNIFTY"] == "SELL"

    # Strategy tag should propagate into meta
    for o in submitted_orders:
        assert o["meta"]["strategy"] == "JOB_TEST"


def test_strategy_job_respects_max_symbols_config():
    wl = FakeWatchlistService(
        {"DAY_SCALP": ["NIFTY", "BANKNIFTY", "FINNIFTY"]}
    )

    ohlcv = FakeOHLCVStore(
        {
            ("NIFTY", "1m"): {"open": 100.0, "close": 101.0},
            ("BANKNIFTY", "1m"): {"open": 200.0, "close": 201.0},
            ("FINNIFTY", "1m"): {"open": 150.0, "close": 151.0},
        }
    )
    fs = FakeFeatureStore(
        {
            ("NIFTY", "1m"): {"screen_score": 1.0},
            ("BANKNIFTY", "1m"): {"screen_score": 1.0},
            ("FINNIFTY", "1m"): {"screen_score": 1.0},
        }
    )
    router = FakeRouter()
    strategy = MomentumIntradayStrategy(config={"min_score": 0.0, "base_size": 1.0})

    job = StrategyJob(
        strategy=strategy,
        router=router,
        watchlists=wl,
        feature_store=fs,
        ohlcv_store=ohlcv,
        config={"watchlist_name": "DAY_SCALP", "timeframe": "1m", "max_symbols": 2},
    )

    submitted = job.run_once()
    assert len(submitted) == 2  # only 2 symbols processed due to max_symbols
    assert len(router.submitted) == 2
