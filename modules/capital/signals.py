from __future__ import annotations

from dataclasses import dataclass
from typing import List

from modules.portfolio.metrics import PortfolioMetricsEngine


@dataclass(frozen=True)
class CapitalSignal:
    name: str
    scale: float
    reason: str

    def clamp(self) -> "CapitalSignal":
        s = min(max(self.scale, 0.0), 1.0)
        return CapitalSignal(self.name, s, self.reason)


class CapitalSignals:
    """
    Independent, monotonic, scale-down-only capital signals.
    """

    @staticmethod
    def drawdown(equities: List[float], max_dd: float, min_scale: float) -> CapitalSignal:
        dds = PortfolioMetricsEngine.drawdowns(equities)
        worst = max(dd.drawdown_pct for dd in dds) if dds else 0.0

        if worst <= 0:
            scale = 1.0
        elif worst >= max_dd:
            scale = min_scale
        else:
            scale = 1.0 - (worst / max_dd) * (1.0 - min_scale)

        return CapitalSignal(
            name="drawdown",
            scale=scale,
            reason=f"DD={worst:.2%}",
        ).clamp()

    @staticmethod
    def volatility(vol: float, vol_cap: float) -> CapitalSignal:
        if vol <= 0:
            scale = 1.0
        elif vol >= vol_cap:
            scale = 0.5
        else:
            scale = 1.0 - (vol / vol_cap) * 0.5

        return CapitalSignal(
            name="volatility",
            scale=scale,
            reason=f"VOL={vol:.4f}",
        ).clamp()

    @staticmethod
    def cash_ratio(cash_ratio: float) -> CapitalSignal:
        if cash_ratio >= 0.5:
            scale = 1.0
        elif cash_ratio <= 0.1:
            scale = 0.3
        else:
            scale = 0.3 + (cash_ratio - 0.1) * (0.7 / 0.4)

        return CapitalSignal(
            name="cash",
            scale=scale,
            reason=f"CASH={cash_ratio:.2f}",
        ).clamp()
