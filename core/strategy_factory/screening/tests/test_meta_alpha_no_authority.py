from decimal import Decimal

from core.strategy_factory.screening.screening_engine import ScreeningEngine
from core.strategy_factory.screening.ensemble_intelligence import (
    StrategyEnsembleIntelligence,
)
from core.strategy_factory.screening.meta_alpha_engine import (
    MetaAlphaIntelligence,
)


def test_meta_alpha_no_mutation():
    engine = ScreeningEngine()
    ensemble = StrategyEnsembleIntelligence()
    meta = MetaAlphaIntelligence()

    base = engine.screen({
        "A": Decimal("1.0"),
        "B": Decimal("2.0"),
    })

    original_hash = base.state_hash
    ensemble_report = ensemble.analyze(screening_result=base)

    meta.analyze(
        screening_result=base,
        ensemble_report=ensemble_report,
    )

    assert base.state_hash == original_hash