from dataclasses import dataclass
from core.regime_detection.regime_types import MarketRegime


@dataclass(frozen=True)
class StrategyRegimeProfile:
    """
    Expected regime compatibility profile of a strategy.
    """

    preferred_regime: MarketRegime


class StrategyRegimeDriftDetector:
    """
    Detects mismatch between current regime and strategy profile.

    Advisory only.
    """

    @staticmethod
    def is_mismatched(
        *, current_regime: MarketRegime, profile: StrategyRegimeProfile
    ) -> bool:
        return current_regime != profile.preferred_regime
