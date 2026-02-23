from decimal import Decimal

from core.strategy_factory.screening.screening_engine import ScreeningEngine
from core.strategy_factory.screening.redundancy_pruner import RedundancyPruner


def test_pruner_contract():
    engine = ScreeningEngine()
    pruner = RedundancyPruner()

    base = engine.screen({
        "A": Decimal("3.0"),
        "B": Decimal("2.0"),
        "C": Decimal("1.0"),
    })

    correlation = {
        ("A", "B"): Decimal("0.9"),
    }

    result = pruner.prune(
        base,
        correlation_matrix=correlation,
        threshold=Decimal("0.8"),
    )

    assert len(result.scores) <= 3
    assert result.state_hash is not None