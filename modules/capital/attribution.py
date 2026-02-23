from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Tuple


@dataclass(frozen=True)
class SignalContribution:
    """
    Contribution of a single signal to capital scaling.
    """
    name: str
    scale: float
    contribution_pct: float  # share of total reduction
    reason: str


@dataclass(frozen=True)
class CapitalAttributionReport:
    """
    Explainability report for a capital decision.
    """
    requested_notional: float
    final_scale: float
    final_notional: float
    dominant_signal: str
    contributions: List[SignalContribution]

    def to_dict(self) -> Dict:
        return {
            "requested_notional": self.requested_notional,
            "final_scale": self.final_scale,
            "final_notional": self.final_notional,
            "dominant_signal": self.dominant_signal,
            "contributions": [
                {
                    "name": c.name,
                    "scale": c.scale,
                    "contribution_pct": round(c.contribution_pct, 4),
                    "reason": c.reason,
                }
                for c in self.contributions
            ],
        }


class CapitalAttributionEngine:
    """
    Phase 13.6 — Capital Attribution & Explainability Engine

    Given individual signal scales and reasons, computes:
    - Final scale
    - Per-signal contribution to reduction
    - Dominant limiting signal
    """

    @staticmethod
    def explain(
        *,
        requested_notional: float,
        signals: Dict[str, Tuple[float, str]],
    ) -> CapitalAttributionReport:
        """
        signals:
            { signal_name: (scale ∈ (0,1], reason) }

        Returns:
            CapitalAttributionReport
        """

        # Defensive normalization
        normalized = {
            name: max(0.0, min(1.0, scale))
            for name, (scale, _) in signals.items()
        }

        # Final scale is multiplicative
        final_scale = 1.0
        for s in normalized.values():
            final_scale *= s

        final_scale = min(final_scale, 1.0)
        final_notional = requested_notional * final_scale

        # Total reduction (for attribution)
        total_reduction = 1.0 - final_scale
        if total_reduction <= 0:
            # No reduction → neutral attribution
            contributions = [
                SignalContribution(
                    name=name,
                    scale=normalized[name],
                    contribution_pct=0.0,
                    reason=signals[name][1],
                )
                for name in signals
            ]
            dominant = "NONE"
        else:
            # Contribution proportional to each signal's log-impact
            impacts: Dict[str, float] = {}
            for name, s in normalized.items():
                # log-impact is additive for multiplicative scales
                impacts[name] = -_safe_log(s)

            total_impact = sum(impacts.values()) or 1.0

            contributions = []
            for name, impact in impacts.items():
                pct = impact / total_impact
                contributions.append(
                    SignalContribution(
                        name=name,
                        scale=normalized[name],
                        contribution_pct=pct,
                        reason=signals[name][1],
                    )
                )

            # Dominant = largest contribution_pct
            dominant = max(contributions, key=lambda c: c.contribution_pct).name

        return CapitalAttributionReport(
            requested_notional=requested_notional,
            final_scale=final_scale,
            final_notional=final_notional,
            dominant_signal=dominant,
            contributions=contributions,
        )


def _safe_log(x: float) -> float:
    """
    Stable log for attribution math.
    """
    if x <= 0:
        return 50.0  # extreme penalty
    import math
    return math.log(x)
