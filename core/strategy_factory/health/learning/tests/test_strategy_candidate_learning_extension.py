from core.strategy_factory.strategy_candidate import StrategyCandidate
from core.strategy_factory.health.learning.strategy_learning_annotation import (
    StrategyLearningAnnotation,
)


def test_strategy_candidate_accepts_learning_annotation():
    annotation = StrategyLearningAnnotation(
        lifecycle_snapshot=None,
        failure_mode_stats=None,
        explanation="historical drawdown risk",
    )

    candidate = StrategyCandidate(
        strategy_id="s1",
        direction="BUY",
        symbols=["NIFTY"],
        probability_score=0.82,
        layers_passed={"fitness": True},
        rationale="strong momentum",
        version="v1",
        learning_annotation=annotation,
    )

    assert candidate.learning_annotation is annotation


def test_strategy_candidate_learning_annotation_optional():
    candidate = StrategyCandidate(
        strategy_id="s2",
        direction="SELL",
        symbols=["BANKNIFTY"],
        probability_score=0.71,
        layers_passed={"fitness": True},
        rationale="mean reversion",
        version="v1",
    )

    assert candidate.learning_annotation is None
