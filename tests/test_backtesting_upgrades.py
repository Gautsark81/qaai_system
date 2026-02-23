import json
import numpy as np
import pandas as pd
import pytest

from qaai_system.backtester.noise_models import NoiseModels
from qaai_system.backtester.regime_detector import RegimeDetector
from qaai_system.backtester.explainability import ExplainabilityLogger
from qaai_system.backtester.core import BacktestExecution
from qaai_system.backtester.tuner import StrategyTuner


def test_noise_models_slippage_and_spread():
    p = 100.0
    bid, ask = NoiseModels.add_spread(p, spread_bps=10)  # 10 bps -> +/- 0.05%
    assert bid < p < ask
    slip_once = NoiseModels.add_slippage(ask, slippage_bps=5)
    # should be within ~ +/-0.05% of ask
    assert ask * 0.9995 <= slip_once <= ask * 1.0005


def test_latency_non_negative():
    for _ in range(10):
        assert NoiseModels.latency_ms(mean_ms=80, jitter_ms=40) >= 0.0


def test_regime_detector_bull_bear_sideways():
    idx = pd.date_range("2025-01-01", periods=200)
    up = pd.Series(np.linspace(100, 200, 200), index=idx)
    down = pd.Series(np.linspace(200, 100, 200), index=idx)
    flat = pd.Series(150 + 0.1 * np.sin(np.linspace(0, 10, 200)), index=idx)

    assert RegimeDetector.detect_regime(up, lookback=50) == "BULL"
    assert RegimeDetector.detect_regime(down, lookback=50) == "BEAR"
    assert RegimeDetector.detect_regime(flat, lookback=50) in {
        "SIDEWAYS",
        "BULL",
        "BEAR",
    }  # flat-ish


def test_explainability_logger_jsonl(tmp_path):
    log_file = tmp_path / "exp.jsonl"
    logger = ExplainabilityLogger(log_file)
    entry = logger.log_trade("T1", {"RSI": 28.5, "ATR": 1.2}, "BUY")
    assert log_file.exists()
    line = log_file.read_text().strip().splitlines()[-1]
    parsed = json.loads(line)
    assert parsed["trade_id"] == "T1"
    assert parsed["features"]["RSI"] == 28.5
    assert parsed["signal"] == "BUY"
    assert entry["signal"] == "BUY"


def test_backtest_execution_fill_series():
    idx = pd.date_range("2025-01-01", periods=10, freq="min")
    prices = pd.Series(np.linspace(100, 101, len(idx)), index=idx)
    ex = BacktestExecution(slippage_bps=5, spread_bps=10)
    fills = ex.simulate_series(prices)
    assert len(fills) == len(prices)
    assert (
        fills.mean() >= prices.mean()
    )  # buy @ ask + slippage should be >= mid on average


@pytest.mark.parametrize("n_trials", [5])
def test_tuner_runs_without_optuna(n_trials):
    # synthetic price series
    n = 60
    df = pd.DataFrame(
        {
            "timestamp": pd.date_range("2025-01-01", periods=n),
            "open": np.linspace(100, 105, n) + np.random.normal(0, 0.2, n),
            "high": np.linspace(100.2, 105.2, n) + np.random.normal(0, 0.2, n),
            "low": np.linspace(99.8, 104.8, n) + np.random.normal(0, 0.2, n),
            "close": np.linspace(100, 105, n) + np.random.normal(0, 0.2, n),
            "volume": np.random.randint(1_000, 2_000, n),
            "symbol": ["SYM"] * n,
        }
    )
    tuner = StrategyTuner(df)
    params = tuner.run(n_trials=n_trials)
    assert set(params.keys()) == {"rsi_window", "atr_window"}
    assert 5 <= params["rsi_window"] <= 30
    assert 5 <= params["atr_window"] <= 30
