from core.strategy_factory.autogen.hypothesis_engine import (
    HypothesisEngine,
    MAX_NEW_CANDIDATES_PER_CYCLE,
)


def test_deterministic_generation():
    engine = HypothesisEngine()

    h1 = engine.generate(regime_score=0.5)
    h2 = engine.generate(regime_score=0.5)

    assert h1 == h2


def test_max_candidates_limit():
    engine = HypothesisEngine()
    hypotheses = engine.generate(regime_score=0.0)

    assert len(hypotheses) <= MAX_NEW_CANDIDATES_PER_CYCLE


def test_regime_classification():
    engine = HypothesisEngine()

    bull = engine.generate(regime_score=0.8)
    bear = engine.generate(regime_score=-0.8)

    assert bull[0].regime_target == "BULL"
    assert bear[0].regime_target == "BEAR"