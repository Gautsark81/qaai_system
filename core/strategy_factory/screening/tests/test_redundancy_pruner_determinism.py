from decimal import Decimal

from core.strategy_factory.screening.screening_engine import ScreeningEngine
from core.strategy_factory.screening.redundancy_pruner import RedundancyPruner


def test_pruner_deterministic():
    engine = ScreeningEngine()
    pruner = RedundancyPruner()

    base = engine.screen({
        "A": Decimal("3.0"),
        "B": Decimal("2.0"),
    })

    correlation = {
        ("A", "B"): Decimal("0.9"),
    }

    r1 = pruner.prune(base, correlation, Decimal("0.8"))
    r2 = pruner.prune(base, correlation, Decimal("0.8"))

    assert r1.state_hash == r2.state_hash