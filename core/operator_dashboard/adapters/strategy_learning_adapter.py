# core/operator_dashboard/adapters/strategy_learning_adapter.py

from typing import Optional, Dict, Any

from core.strategy_factory.strategy_candidate import StrategyCandidate
from core.strategy_factory.health.learning.strategy_learning_annotation import (
    StrategyLearningAnnotation,
)


class StrategyLearningAdapter:
    """
    Read-only adapter exposing strategy learning annotations
    for operator dashboards and explainability surfaces.

    This adapter MUST:
    - Never mutate candidates
    - Never access registries
    - Be safe when learning is absent
    """

    def from_candidate(self, candidate: StrategyCandidate) -> Dict[str, Any]:
        annotation: Optional[StrategyLearningAnnotation] = getattr(
            candidate, "learning_annotation", None
        )

        if annotation is None:
            return {"learning_annotation": None}

        return {
            "learning_annotation": {
                "explanation": annotation.explanation,
                "failure_mode_stats": annotation.failure_mode_stats,
                "lifecycle_snapshot": annotation.lifecycle_snapshot,
            }
        }
