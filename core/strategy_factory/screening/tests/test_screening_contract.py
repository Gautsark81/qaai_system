from decimal import Decimal

from core.strategy_factory.screening.screening_engine import ScreeningEngine


def test_screening_contract_structure():
    engine = ScreeningEngine()

    result = engine.screen({
        "A": Decimal("1.0"),
        "B": Decimal("2.0"),
    })

    assert len(result.scores) == 2
    assert result.state_hash is not None