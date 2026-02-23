from __future__ import annotations

from dataclasses import dataclass

from modules.regime.detector import RegimeDetector, RegimeFeatures
from modules.regime.policy import RegimePolicy


@dataclass(frozen=True)
class RegimeSignal:
    """
    Advisory capital signal derived from market regime.
    """

    policy: RegimePolicy = RegimePolicy()

    def evaluate(self, *, features: RegimeFeatures) -> tuple[float, str]:
        regime = RegimeDetector.detect(features)
        scale = self.policy.scale_for(regime)

        reason = (
            f"REGIME={regime.upper()} "
            f"(vol={features.volatility:.3f}, "
            f"trend={features.trend_strength:.2f}, "
            f"dd={features.drawdown_pct:.2%})"
        )

        return scale, reason
