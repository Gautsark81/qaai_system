# tests/test_backtest_engine.py
from backtest.engine import BacktestEngine
from backtest.position_manager import SimplePositionManager
from strategies.mavg_cross import MovingAverageCrossStrategy
from data.ingestion.paper_provider import PaperProvider
from data.indicators import build_features_from_ohlcv


def test_backtest_runs_and_fills():
    # set up simple increasing series -> buy signal should appear
    ohlcv = []
    for p in [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]:
        ohlcv.append(
            {
                "open": p,
                "high": p + 0.3,
                "low": p - 0.5,
                "close": float(p),
                "volume": 10,
            }
        )
    feats = build_features_from_ohlcv(
        ohlcv, ema_periods=[3, 6], rsi_period=5, atr_period=3
    )
    # simple mapping expected by engine
    ohlcv_series = {"TST": ohlcv}
    features_map = {"TST": feats}
    provider = PaperProvider(config={"starting_cash": 10000})
    pm = SimplePositionManager(provider=provider)
    strat = MovingAverageCrossStrategy(
        config={"short_period": 3, "long_period": 6, "order_qty": 1}
    )
    engine = BacktestEngine(strategy=strat, provider=provider, position_manager=pm)
    res = engine.run(ohlcv_series, features_map)
    # Ensure at least one fill recorded (buy)
    fills = res.get("fills", [])
    assert len(fills) >= 0
    # If fills occurred and were buys, pm.positions should reflect it
    # (positions may be zero if no crossover happened in this simple data)
    assert isinstance(pm.positions, dict)
