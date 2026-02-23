from decimal import Decimal
from core.strategy_factory.screening.screening_engine import ScreeningEngine
from core.strategy_factory.screening.ensemble_intelligence import (
    StrategyEnsembleIntelligence,
)


def test_ensemble_contract_structure():
    engine = ScreeningEngine()
    ensemble = StrategyEnsembleIntelligence()

    base = engine.screen({
        "A": Decimal("1.0"),
        "B": Decimal("2.0"),
    })

    report = ensemble.analyze(screening_result=base)

    assert report.state_hash is not None
    assert len(report.signals) == 3