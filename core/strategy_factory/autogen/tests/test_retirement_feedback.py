from core.strategy_factory.autogen.candidate_registry import CandidateRegistry
from core.strategy_factory.autogen.candidate_models import CandidateStage
from core.strategy_factory.autogen.hypothesis_engine import HypothesisEngine
from core.strategy_factory.autogen.hypothesis_models import StrategyHypothesis
from core.strategy_factory.autogen.retirement_feedback import (
    RetirementFeedbackEngine,
)


def test_feature_penalty_applies():

    registry = CandidateRegistry()
    feedback = RetirementFeedbackEngine(registry)

    hypothesis = StrategyHypothesis(
        hypothesis_id="H1",
        version=1,
        feature_set={"momentum": 1.0},
        entry_logic="cross",
        exit_logic="fixed",
        timeframe="1h",
        regime_target="BULL",
    )

    registry.register_lab_candidate("H1", hypothesis.compute_hash())
    registry.update_stage("H1", CandidateStage.RETIRED, ssr=60)

    feedback.capture_retirement(hypothesis)

    engine = HypothesisEngine(feedback_engine=feedback)

    hypotheses = engine.generate(regime_score=0.8)

    penalized = [
        h for h in hypotheses if "momentum" in h.feature_set
    ][0]

    assert penalized.feature_set["momentum"] < 1.2