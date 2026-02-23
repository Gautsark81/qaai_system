# core/strategy_factory/autogen/retirement_feedback.py

from dataclasses import dataclass
from typing import Dict, List
from collections import defaultdict

from .candidate_registry import CandidateRegistry
from .candidate_models import CandidateStage
from .hypothesis_models import StrategyHypothesis


@dataclass(frozen=True)
class FailureRecord:
    hypothesis_id: str
    regime_target: str
    dominant_feature: str
    ssr: float
    max_drawdown: float


class RetirementFeedbackEngine:

    def __init__(self, registry: CandidateRegistry):
        self.registry = registry
        self._failure_memory: List[FailureRecord] = []
        self._feature_penalty: Dict[str, int] = defaultdict(int)

    # --------------------------------------------------
    # Capture failure at retirement
    # --------------------------------------------------
    def capture_retirement(self, hypothesis: StrategyHypothesis):

        latest = self.registry.get_latest(hypothesis.hypothesis_id)

        if latest is None:
            raise ValueError("Candidate not found")

        if latest.stage != CandidateStage.RETIRED:
            raise ValueError("Only RETIRED candidates can be captured")

        dominant_feature = next(iter(hypothesis.feature_set.keys()))

        record = FailureRecord(
            hypothesis_id=hypothesis.hypothesis_id,
            regime_target=hypothesis.regime_target,
            dominant_feature=dominant_feature,
            ssr=latest.ssr or 0.0,
            max_drawdown=latest.max_drawdown or 0.0,
        )

        self._failure_memory.append(record)
        self._feature_penalty[dominant_feature] += 1

    # --------------------------------------------------
    # Provide penalty score for hypothesis engine
    # --------------------------------------------------
    def get_feature_penalty(self, feature: str) -> float:

        penalty_count = self._feature_penalty.get(feature, 0)

        # deterministic penalty scaling
        return min(0.5, penalty_count * 0.1)

    # --------------------------------------------------
    # Expose failure history (read-only)
    # --------------------------------------------------
    def failure_history(self) -> List[FailureRecord]:
        return list(self._failure_memory)