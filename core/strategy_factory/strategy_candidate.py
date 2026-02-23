from dataclasses import dataclass
from typing import Dict, List, Optional

from core.strategy_factory.health.learning.strategy_learning_annotation import (
    StrategyLearningAnnotation,
)


@dataclass(frozen=True)
class StrategyCandidate:
    """
    Tournament-only strategy candidate.

    learning_annotation is OPTIONAL and advisory-only.
    It does not affect ranking, selection, or execution.
    """

    strategy_id: str
    direction: str
    symbols: List[str]
    probability_score: float
    layers_passed: Dict[str, bool]
    rationale: str
    version: str

    # --- Phase 11.9-B ---
    learning_annotation: Optional[StrategyLearningAnnotation] = None
