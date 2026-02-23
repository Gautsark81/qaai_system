from decimal import Decimal
from core.strategy_factory.screening.screening_engine import ScreeningEngine
from core.strategy_factory.screening.ensemble_intelligence import (
    StrategyEnsembleIntelligence,
)


def test_ensemble_deterministic():
    engine = ScreeningEngine()
    ensemble = StrategyEnsembleIntelligence()

    base = engine.screen({
        "A": Decimal("1.0"),
        "B": Decimal("2.0"),
    })

    r1 = ensemble.analyze(screening_result=base)
    r2 = ensemble.analyze(screening_result=base)

    assert r1.state_hash == r2.state_hash