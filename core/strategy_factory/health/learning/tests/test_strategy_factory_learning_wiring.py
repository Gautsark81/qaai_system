from core.strategy_factory.health.learning.strategy_learning_annotation import (
    StrategyLearningAnnotation,
)
from core.strategy_factory.health.learning.learning_registry import LearningRegistry
from core.strategy_factory.strategy_emitter import StrategyEmitter
from core.strategy_factory.strategy_candidate import StrategyCandidate


def test_strategy_factory_attaches_learning_annotation_when_available():
    registry = LearningRegistry()
    emitter = StrategyEmitter(learning_registry=registry)

    annotation = StrategyLearningAnnotation(
        lifecycle_snapshot=None,
        failure_mode_stats=None,
        explanation="historical drawdown risk",
    )

    registry._latest_annotation = annotation  # test hook only

    candidate = emitter.emit(
        strategy_id="s1",
        direction="BUY",
        symbols=["NIFTY"],
        probability_score=0.85,
        layers_passed={"fitness": True},
        rationale="trend aligned",
        version="v1",
    )

    assert isinstance(candidate, StrategyCandidate)
    assert candidate.learning_annotation is annotation
