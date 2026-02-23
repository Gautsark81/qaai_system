from __future__ import annotations
from typing import List
from math import log
from .contracts import AlphaDecayReport


class AlphaDecayAnalyzer:
    """
    v2.1 Alpha Decay Analyzer

    Design principles:
    - Detect decay EARLY (governance-first)
    - Deterministic, side-effect free
    - Conservative thresholds (no optimism bias)
    """

    def analyze(
        self,
        strategy_id: str,
        scores: List[float],
        days_between: int,
    ) -> AlphaDecayReport:

        if len(scores) < 2:
            return AlphaDecayReport(
                strategy_id=strategy_id,
                half_life_days=float("inf"),
                decay_rate=0.0,
                status="STABLE",
            )

        # Numerical safety
        start = max(scores[0], 1e-6)
        end = max(scores[-1], 1e-6)

        periods = max(1, (len(scores) - 1) * days_between)

        # Exponential decay rate
        decay_rate = max(
            0.0,
            (log(start) - log(end)) / periods,
        )

        # Half-life calculation
        if decay_rate == 0:
            half_life = float("inf")
        else:
            half_life = log(2) / decay_rate

        # 🔒 v2.1 GOVERNANCE THRESHOLDS
        if decay_rate >= 0.04:
            status = "CRITICAL"
        elif decay_rate >= 0.015:
            status = "DECAYING"
        else:
            status = "STABLE"

        return AlphaDecayReport(
            strategy_id=strategy_id,
            half_life_days=half_life,
            decay_rate=decay_rate,
            status=status,
        )
