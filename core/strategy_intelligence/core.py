# core/strategy_intelligence/core.py

from typing import Iterable

from .verdict import StrategyIntelligenceVerdict


class StrategyIntelligence:
    """
    Diagnostic-only strategy intelligence.
    No execution, no capital, no mutation.
    """

    def __init__(self, strategy_id: str) -> None:
        self.strategy_id = strategy_id

    def evaluate(self, results: Iterable) -> StrategyIntelligenceVerdict:
        """
        Evaluate realized strategy outcomes and emit a diagnostic verdict.
        """
        results = tuple(results)
        total = len(results)

        # --- SSR computation (deterministic) ---
        if total == 0:
            ssr = 0.0
        else:
            successes = sum(1 for r in results if getattr(r, "success", False))
            ssr = successes / total

        # --- Structural instability detection ---
        # UNSTABLE = alternating success/failure pattern (high variance behavior)
        unstable_pattern = False
        if total >= 4:
            flags = [bool(getattr(r, "success", False)) for r in results]
            unstable_pattern = all(
                flags[i] != flags[i - 1] for i in range(1, len(flags))
            )

        # --- Health classification ---
        if unstable_pattern:
            health = "UNSTABLE"
        elif ssr >= 0.8:
            health = "HEALTHY"
        else:
            health = "DEGRADING"

        # --- Advisory-only promotion signal ---
        promotion_signal = "PROMOTION_ELIGIBLE" if health == "HEALTHY" else "NONE"

        return StrategyIntelligenceVerdict(
            strategy_id=self.strategy_id,
            health=health,
            ssr=ssr,
            promotion_signal=promotion_signal,
        )
