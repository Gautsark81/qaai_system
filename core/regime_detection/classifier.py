from .features import RegimeFeatures
from .regime_types import MarketRegime


class RegimeClassifier:
    """
    Deterministic regime classifier.

    No learning.
    No state.
    No execution authority.
    """

    @staticmethod
    def classify(features: RegimeFeatures) -> MarketRegime:
        if features.volatility > 0.7 and features.trend_strength < 0.3:
            return MarketRegime.VOLATILE

        if features.trend_strength > 0.7:
            return MarketRegime.TRENDING

        if features.range_ratio > 0.7:
            return MarketRegime.RANGE_BOUND

        if features.trend_strength < 0.3:
            return MarketRegime.MEAN_REVERTING

        return MarketRegime.UNKNOWN
