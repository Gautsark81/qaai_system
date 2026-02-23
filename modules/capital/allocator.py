from __future__ import annotations

from dataclasses import dataclass
from typing import List

from modules.capital.decision import CapitalDecision
from modules.capital.policies import CapitalPolicy
from modules.portfolio.metrics import PortfolioMetricsEngine


@dataclass(frozen=True)
class CapitalAllocator:
    """
    Phase 13.2 — Capital Allocator (Advanced, Advisory Only)

    This allocator:
    - Consumes portfolio metrics
    - Applies MULTIPLE independent capital throttles
    - Aggregates them conservatively
    - NEVER increases exposure
    """

    policy: CapitalPolicy = CapitalPolicy()

    def allocate(
        self,
        *,
        equities: List[float],
        requested_notional: float,
        volatility: float | None = None,
        cash_ratio: float | None = None,
    ) -> CapitalDecision:

        # -----------------------------
        # Hard defensive checks
        # -----------------------------
        if requested_notional <= 0:
            return CapitalDecision(
                approved=False,
                max_notional=0.0,
                scale_factor=0.0,
                reason="Invalid requested notional",
            )

        scales: list[tuple[str, float]] = []

        # -----------------------------
        # 1. Drawdown-based scaling
        # -----------------------------
        dds = PortfolioMetricsEngine.drawdowns(equities)
        worst_dd = max(dd.drawdown_pct for dd in dds) if dds else 0.0

        if worst_dd <= 0:
            dd_scale = 1.0
        elif worst_dd >= self.policy.max_drawdown_pct:
            dd_scale = self.policy.min_scale
        else:
            frac = worst_dd / self.policy.max_drawdown_pct
            dd_scale = 1.0 - frac * (1.0 - self.policy.min_scale)

        dd_scale = self.policy.clamp_scale(dd_scale)
        scales.append(("DD", dd_scale))

        # -----------------------------
        # 2. Volatility throttle (soft)
        # -----------------------------
        if volatility is not None:
            if volatility >= self.policy.volatility_cap:
                vol_scale = self.policy.volatility_min_scale
            else:
                frac = volatility / self.policy.volatility_cap
                vol_scale = 1.0 - frac * (1.0 - self.policy.volatility_min_scale)

            scales.append(("VOL", vol_scale))

        # -----------------------------
        # 3. Cash / liquidity throttle
        # -----------------------------
        if cash_ratio is not None:
            if cash_ratio <= self.policy.min_cash_ratio:
                cash_scale = self.policy.cash_min_scale
            else:
                cash_scale = 1.0

            scales.append(("CASH", cash_scale))

        # -----------------------------
        # Aggregate (multiplicative)
        # -----------------------------
        final_scale = 1.0
        reasons = []

        for name, s in scales:
            final_scale *= s
            reasons.append(f"{name}={s:.2f}")

        final_scale = self.policy.clamp_scale(final_scale)
        max_notional = requested_notional * final_scale

        # -----------------------------
        # Absolute safety caps
        # -----------------------------
        if self.policy.hard_cap_notional is not None:
            max_notional = min(max_notional, self.policy.hard_cap_notional)

        # Scale-down only (hard guarantee)
        if max_notional > requested_notional:
            max_notional = requested_notional
            final_scale = 1.0

        return CapitalDecision(
            approved=True,
            max_notional=max_notional,
            scale_factor=final_scale,
            reason=" × ".join(reasons),
        )
