# core/strategy_factory/health/health_builder.py

from core.strategy_factory.health.ssr_engine import SSREngine
from core.strategy_factory.health.snapshot import StrategyHealthSnapshot


class StrategyHealthBuilder:
    """
    Pure builder for StrategyHealthSnapshot (SSR-focused).

    Principles:
    - Stateless
    - Deterministic
    - No lifecycle authority
    - No side effects
    """

    @staticmethod
    def build(
        *,
        performance_score: float,
        risk_score: float,
        stability_score: float,
    ) -> StrategyHealthSnapshot:
        """
        Construct a StrategyHealthSnapshot from component scores.
        """

        # --- Normalize inputs ---
        performance = float(performance_score)
        risk = float(risk_score)
        stability = float(stability_score)

        components = {
            "performance": performance,
            "risk": risk,
            "stability": stability,
        }

        # --- Compute SSR ---
        ssr = SSREngine.compute(components=components)

        # --- Build immutable snapshot ---
        snapshot = StrategyHealthSnapshot(
            performance_score=performance,
            risk_score=risk,
            stability_score=stability,
            ssr=ssr,
            ssr_components=components,
        )

        return snapshot
