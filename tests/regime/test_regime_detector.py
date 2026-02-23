from modules.regime.detector import RegimeDetector, RegimeFeatures


def test_calm_trend_detection():
    f = RegimeFeatures(volatility=0.02, trend_strength=0.7, drawdown_pct=0.05)
    assert RegimeDetector.detect(f) == "calm_trend"


def test_volatile_trend_detection():
    f = RegimeFeatures(volatility=0.035, trend_strength=0.6, drawdown_pct=0.08)
    assert RegimeDetector.detect(f) == "volatile_trend"


def test_panic_detection():
    f = RegimeFeatures(volatility=0.05, trend_strength=0.3, drawdown_pct=0.25)
    assert RegimeDetector.detect(f) == "panic"


def test_choppy_detection():
    f = RegimeFeatures(volatility=0.02, trend_strength=0.2, drawdown_pct=0.05)
    assert RegimeDetector.detect(f) == "choppy"
