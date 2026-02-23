from core.strategy_factory.strategy_candidate import StrategyCandidate
from core.strategy_factory.health.learning.strategy_learning_annotation import (
    StrategyLearningAnnotation,
)
from core.operator_dashboard.adapters.strategy_learning_adapter import (
    StrategyLearningAdapter,
)


def test_strategy_learning_adapter_exposes_annotation():
    annotation = StrategyLearningAnnotation(
        lifecycle_snapshot=None,
        failure_mode_stats=None,
        explanation="historical drawdown risk",
    )

    candidate = StrategyCandidate(
        strategy_id="s1",
        direction="BUY",
        symbols=["NIFTY"],
        probability_score=0.9,
        layers_passed={"fitness": True},
        rationale="trend",
        version="v1",
        learning_annotation=annotation,
    )

    adapter = StrategyLearningAdapter()

    payload = adapter.from_candidate(candidate)

    assert payload["learning_annotation"]["explanation"] == "historical drawdown risk"


def test_strategy_learning_adapter_handles_missing_annotation():
    candidate = StrategyCandidate(
        strategy_id="s2",
        direction="SELL",
        symbols=["BANKNIFTY"],
        probability_score=0.6,
        layers_passed={"fitness": True},
        rationale="mean reversion",
        version="v1",
    )

    adapter = StrategyLearningAdapter()

    payload = adapter.from_candidate(candidate)

    assert payload["learning_annotation"] is None
