from modules.regime.signal import RegimeSignal
from modules.regime.detector import RegimeFeatures


def test_regime_signal_outputs_scale_and_reason():
    signal = RegimeSignal()
    features = RegimeFeatures(
        volatility=0.04,
        trend_strength=0.6,
        drawdown_pct=0.10,
    )

    scale, reason = signal.evaluate(features=features)

    assert 0.0 < scale <= 1.0
    assert "REGIME=" in reason
