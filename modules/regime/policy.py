from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RegimePolicy:
    """
    Maps regimes to capital multipliers.

    All values are conservative by default.
    """
    calm_trend: float = 1.00
    volatile_trend: float = 0.75
    choppy: float = 0.60
    panic: float = 0.25

    def scale_for(self, regime: str) -> float:
        return {
            "calm_trend": self.calm_trend,
            "volatile_trend": self.volatile_trend,
            "choppy": self.choppy,
            "panic": self.panic,
        }.get(regime, self.choppy)
