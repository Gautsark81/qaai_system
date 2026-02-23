from datetime import datetime

from core.ssr.aggregator import SSRAggregator
from core.ssr.components.outcome_quality import OutcomeQualityComponent
from core.ssr.components.health_stability import HealthStabilityComponent
from core.ssr.components.consistency import ConsistencyComponent
from core.ssr.versions import SSR_ENGINE_V1


class SSREngine:
    """
    Orchestrates SSR computation end-to-end.

    This engine is PURE:
    - No IO
    - No persistence
    - Deterministic given inputs
    """

    def __init__(self):
        self.aggregator = SSRAggregator()

        # Fixed component set (v1)
        self.components = [
            OutcomeQualityComponent(weight=1.0),
            HealthStabilityComponent(weight=1.0),
            ConsistencyComponent(weight=1.0),
        ]

    def compute(
        self,
        *,
        strategy_id: str,
        as_of: datetime,
        outcome_inputs: dict,
        health_inputs: dict,
        consistency_inputs: dict,
        trailing_metrics: dict[str, float],
        confidence: float,
    ):
        component_scores = []

        for comp in self.components:
            if comp.name == "outcome_quality":
                score = comp.compute(inputs=outcome_inputs)

            elif comp.name == "health_stability":
                score = comp.compute(inputs=health_inputs)

            elif comp.name == "consistency":
                score = comp.compute(inputs=consistency_inputs)

            else:
                raise RuntimeError(f"Unknown SSR component: {comp.name}")

            component_scores.append(score)

        return self.aggregator.aggregate(
            strategy_id=strategy_id,
            as_of=as_of,
            components=component_scores,
            trailing_metrics=dict(trailing_metrics),
            confidence=confidence,
            version=SSR_ENGINE_V1,
        )
