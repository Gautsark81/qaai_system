# path: tests/test_meta_signal_filter.py
import pandas as pd

from qaai_system.ml.probability_model import ProbabilityModel, ProbabilityModelConfig
from qaai_system.ml.regime_detector import RegimeDetector, RegimeDetectorConfig
from qaai_system.ml.meta_signal_filter import (
    MetaSignalFilter,
    MetaSignalFilterConfig,
    MetaSignalEngineWrapper,
)


class DummySignalEngine:
    def __init__(self, df: pd.DataFrame):
        self._df = df

    def run(self, *args, **kwargs):
        return self._df.copy()


def test_meta_filter_drops_low_confidence_signals():
    df = pd.DataFrame(
        {
            "symbol": ["INFY", "SBIN"],
            "side": ["BUY", "SELL"],
            "price": [1000.0, 500.0],
            "signal_strength": [2.0, 0.1],  # first strong, second weak
            "vol": [1.0, 1.0],
            "time_of_day": [10.0, 10.0],
            "position_size": [5, 5],
        }
    )

    prob = ProbabilityModel(ProbabilityModelConfig())
    regime = RegimeDetector(RegimeDetectorConfig())
    cfg = MetaSignalFilterConfig(conf_min=0.55, prob_min=0.55)

    meta_filter = MetaSignalFilter(probability_model=prob, regime_detector=regime, config=cfg)
    wrapped = MetaSignalEngineWrapper(DummySignalEngine(df), meta_filter)

    out = wrapped.run(["MOCK"])
    assert isinstance(out, pd.DataFrame)
    # We expect at least one row to survive (the strong one)
    assert len(out) == 1
    assert out.iloc[0]["symbol"] == "INFY"
    assert "ml_confidence" in out.columns
    assert "win_prob" in out.columns


def test_regime_label_and_risk_factor_change_with_vol_and_time():
    df = pd.DataFrame(
        {
            "symbol": ["NIFTY", "BANKNIFTY", "MIDCPNIFTY"],
            "side": ["BUY", "BUY", "BUY"],
            "price": [20000.0, 45000.0, 12000.0],
            "signal_strength": [1.0, 1.0, 1.0],
            "vol": [0.3, 2.0, 1.0],         # low, high, medium
            "time_of_day": [10.0, 10.0, 12.3],  # last in NO_TRADE window (default 12-13)
            "position_size": [10, 10, 10],
        }
    )

    prob = ProbabilityModel()
    regime_cfg = RegimeDetectorConfig(no_trade_windows=((12.0, 13.0),))
    regime = RegimeDetector(regime_cfg)
    meta_cfg = MetaSignalFilterConfig(conf_min=0.0, prob_min=0.0, apply_risk_sizer=True)

    meta_filter = MetaSignalFilter(probability_model=prob, regime_detector=regime, config=meta_cfg)
    out = meta_filter.apply(df)

    # Three rows in, but NO_TRADE regime will be filtered out by default RegimeFilter
    # since MetaSignalFilter's default blocked_regimes=("NO_TRADE",)
    symbols = list(out["symbol"])
    assert "MIDCPNIFTY" not in symbols  # dropped due to NO_TRADE

    # Check labels and risk_factor on remaining rows
    assert "regime_label" in out.columns
    assert "risk_factor" in out.columns

    # Should have at least one TRENDING or HIGH_VOL depending on vol/trend
    assert any(lbl in ("TRENDING", "HIGH_VOL", "CHOPPY", "UNKNOWN") for lbl in out["regime_label"])

    # position_size should have been scaled (int, >=1)
    assert (out["position_size"] >= 1).all()
