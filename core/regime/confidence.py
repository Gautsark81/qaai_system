from dataclasses import dataclass
from typing import Dict

from core.regime.taxonomy import MarketRegime


@dataclass(frozen=True)
class RegimeConfidencePolicy:
    """
    Defines confidence scaling per regime.

    Multipliers must be in [0.0, 1.0].
    """
    multipliers: Dict[MarketRegime, float]

    def multiplier_for(self, regime: MarketRegime) -> float:
        return self.multipliers.get(regime, 0.0)


def gate_confidence(
    *,
    raw_confidence: float,
    regime: MarketRegime,
    policy: RegimeConfidencePolicy,
) -> float:
    """
    Compute effective confidence after regime-aware gating.

    Guarantees:
    - output in [0.0, 1.0]
    - deterministic
    """

    raw = max(0.0, min(1.0, raw_confidence))
    multiplier = max(0.0, min(1.0, policy.multiplier_for(regime)))

    return raw * multiplier
