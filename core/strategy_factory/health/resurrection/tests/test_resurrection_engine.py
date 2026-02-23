from core.strategy_factory.health.resurrection.engine import ResurrectionEngine


def test_engine_creates_candidate(registry, record, decay):
    engine = ResurrectionEngine(registry)

    candidate = engine.evaluate(record, decay)

    assert candidate is not None
    assert candidate.state == "RESURRECTION_CANDIDATE"
