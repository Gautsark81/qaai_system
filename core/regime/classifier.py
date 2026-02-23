from typing import Dict

from core.regime.taxonomy import (
    VolatilityRegime,
    TrendRegime,
    MarketRegime,
)

# =====================================================
# V3.1 — Pure Regime Taxonomy Classifiers (FINAL)
# =====================================================

def classify_trend(trend_strength: float) -> TrendRegime:
    """
    Trend regime is binary by design:
    - TRENDING_UP
    - RANGE

    Directional sign is a strategy concern, not regime.
    """
    if trend_strength > 0.3:
        return TrendRegime.TRENDING_UP
    return TrendRegime.RANGE


def classify_volatility(volatility_ratio: float) -> VolatilityRegime:
    """
    Classifies volatility regime.
    STRICTLY aligned to VolatilityRegime enum.
    """
    if volatility_ratio > 1.2:
        return VolatilityRegime.HIGH
    return VolatilityRegime.LOW


def classify_market_regime(
    *,
    trend_strength: float,
    volatility_ratio: float,
    correlation_stress: float,
) -> MarketRegime:
    """
    Canonical market regime classifier.

    Deterministic.
    Explainable.
    Signal-free.
    Enum-faithful.
    """

    # Correlation stress dominates all regimes
    if correlation_stress > 0.8:
        return MarketRegime.CHAOTIC

    trend = classify_trend(trend_strength)
    vol = classify_volatility(volatility_ratio)

    if trend == TrendRegime.RANGE:
        return (
            MarketRegime.RANGE_LOW_VOL
            if vol == VolatilityRegime.LOW
            else MarketRegime.RANGE_HIGH_VOL
        )

    return (
        MarketRegime.TREND_LOW_VOL
        if vol == VolatilityRegime.LOW
        else MarketRegime.TREND_HIGH_VOL
    )


# =====================================================
# V3.1 — Structured Regime Snapshot (NO SIGNALS)
# =====================================================

def classify_regime_snapshot(
    *,
    trend_strength: float,
    volatility_ratio: float,
    correlation_stress: float,
) -> Dict[str, str]:
    """
    Returns a structured, immutable-friendly regime snapshot.
    """

    trend = classify_trend(trend_strength)
    vol = classify_volatility(volatility_ratio)
    market = classify_market_regime(
        trend_strength=trend_strength,
        volatility_ratio=volatility_ratio,
        correlation_stress=correlation_stress,
    )

    return {
        "trend": trend.name,
        "volatility": vol.name,
        "market": market.name,
    }
