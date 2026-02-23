from dataclasses import dataclass
from .regime_types import MarketRegime


@dataclass(frozen=True)
class RegimeSnapshot:
    """
    Immutable advisory snapshot of detected market regime.

    This object is intended for:
    - dashboards
    - diagnostics
    - strategy advisory context
    """

    timestamp: int
    regime: MarketRegime
    confidence: float
