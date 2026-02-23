from typing import Dict, List, Optional

from core.strategy_factory.strategy_candidate import StrategyCandidate
from core.strategy_factory.health.learning.learning_registry import LearningRegistry


class StrategyEmitter:
    """
    Emits StrategyCandidate objects for downstream factory stages.

    learning_registry is OPTIONAL and advisory-only.
    """

    def __init__(
        self,
        *,
        learning_registry: Optional[LearningRegistry] = None,
    ):
        self._learning_registry = learning_registry

    def emit(
        self,
        *,
        strategy_id: str,
        direction: str,
        symbols: List[str],
        probability_score: float,
        layers_passed: Dict[str, bool],
        rationale: str,
        version: str,
    ) -> StrategyCandidate:

        learning_annotation = None
        if self._learning_registry is not None:
            # advisory read-only hook
            learning_annotation = self._learning_registry.latest_annotation()

        return StrategyCandidate(
            strategy_id=strategy_id,
            direction=direction,
            symbols=symbols,
            probability_score=probability_score,
            layers_passed=layers_passed,
            rationale=rationale,
            version=version,
            learning_annotation=learning_annotation,
        )
