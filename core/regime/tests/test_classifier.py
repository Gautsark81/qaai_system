from core.regime.classifier import (
    classify_trend,
    classify_volatility,
    classify_market_regime,
)
from core.regime.taxonomy import (
    TrendRegime,
    VolatilityRegime,
    MarketRegime,
)


def test_classify_trend():
    assert classify_trend(0.6) == TrendRegime.TRENDING_UP
    assert classify_trend(-0.6) == TrendRegime.RANGE
    assert classify_trend(0.0) == TrendRegime.RANGE


def test_classify_volatility():
    assert classify_volatility(0.6) == VolatilityRegime.LOW
    assert classify_volatility(1.0) == VolatilityRegime.LOW
    assert classify_volatility(1.5) == VolatilityRegime.HIGH


def test_classify_market_regime_trend_low_vol():
    regime = classify_market_regime(
        trend_strength=0.7,
        volatility_ratio=0.7,
        correlation_stress=0.1,
    )
    assert regime == MarketRegime.TREND_LOW_VOL


def test_classify_market_regime_range_high_vol():
    regime = classify_market_regime(
        trend_strength=0.0,
        volatility_ratio=1.6,
        correlation_stress=0.1,
    )
    assert regime == MarketRegime.RANGE_HIGH_VOL


def test_classify_market_regime_chaotic_override():
    regime = classify_market_regime(
        trend_strength=0.9,
        volatility_ratio=0.5,
        correlation_stress=0.95,
    )
    assert regime == MarketRegime.CHAOTIC
