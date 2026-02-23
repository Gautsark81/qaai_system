from decimal import Decimal

from core.strategy_factory.screening.screening_engine import ScreeningEngine
from core.strategy_factory.screening.ensemble_intelligence import (
    StrategyEnsembleIntelligence,
)
from core.strategy_factory.screening.meta_alpha_engine import (
    MetaAlphaIntelligence,
)


def test_meta_alpha_deterministic():
    engine = ScreeningEngine()
    ensemble = StrategyEnsembleIntelligence()
    meta = MetaAlphaIntelligence()

    base = engine.screen({
        "A": Decimal("1.0"),
        "B": Decimal("2.0"),
    })

    ensemble_report = ensemble.analyze(screening_result=base)

    r1 = meta.analyze(
        screening_result=base,
        ensemble_report=ensemble_report,
    )
    r2 = meta.analyze(
        screening_result=base,
        ensemble_report=ensemble_report,
    )

    assert r1.state_hash == r2.state_hash