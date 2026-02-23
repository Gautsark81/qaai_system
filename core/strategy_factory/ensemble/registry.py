from typing import List
from .models import EnsembleStrategy


class EnsembleRegistry:
    """
    Promotion-only deterministic registry.
    Accepts pre-validated promoted strategies.
    """

    MIN_SSR = 80.0

    @staticmethod
    def load(promoted_strategies: List[dict]) -> List[EnsembleStrategy]:
        eligible = [
            EnsembleStrategy(
                strategy_id=s["strategy_id"],
                ssr=s["ssr"],
                drawdown_pct=s.get("drawdown_pct", 0.0),
            )
            for s in promoted_strategies
            if s["ssr"] >= EnsembleRegistry.MIN_SSR
        ]

        # deterministic ordering
        eligible.sort(key=lambda s: s.strategy_id)
        return eligible