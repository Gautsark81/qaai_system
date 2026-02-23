from __future__ import annotations

from dataclasses import dataclass

from modules.capital.decision import CapitalDecision


@dataclass(frozen=True)
class PortfolioExecutionGuard:
    """
    Phase 13.5 — Portfolio-Aware Execution Guard

    Applies CapitalDecision safely:
    - scale-down only
    - advisory only
    - never increases exposure
    - never overrides RiskManager
    """

    def apply(
        self,
        *,
        requested_notional: float,
        decision: CapitalDecision,
    ) -> float:
        """
        Returns the allowed notional after applying capital intelligence.
        """
        if not decision.approved:
            return 0.0

        # Absolute safety: never exceed requested
        allowed = min(requested_notional, decision.max_notional)

        # Never negative
        return max(0.0, allowed)
