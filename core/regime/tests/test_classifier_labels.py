from core.regime.classifier import classify_market_regime
from core.regime.taxonomy import MarketRegime


def test_trend_low_vol():
    regime = classify_market_regime(
        trend_strength=0.6,
        volatility_ratio=0.6,
        correlation_stress=0.2,
    )
    assert regime == MarketRegime.TREND_LOW_VOL


def test_range_high_vol():
    regime = classify_market_regime(
        trend_strength=0.0,
        volatility_ratio=1.5,
        correlation_stress=0.2,
    )
    assert regime == MarketRegime.RANGE_HIGH_VOL


def test_chaotic_override():
    regime = classify_market_regime(
        trend_strength=0.9,
        volatility_ratio=0.5,
        correlation_stress=0.95,
    )
    assert regime == MarketRegime.CHAOTIC
