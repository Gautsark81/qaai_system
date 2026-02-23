from dataclasses import dataclass


@dataclass(frozen=True)
class RegimeFeatures:
    """
    Read-only feature vector for regime classification.

    All values must be precomputed upstream.
    """

    volatility: float
    trend_strength: float
    range_ratio: float
