from decimal import Decimal

from core.strategy_factory.screening.screening_engine import ScreeningEngine


def test_order_independent_input():
    engine = ScreeningEngine()

    r1 = engine.screen({
        "A": Decimal("1.0"),
        "B": Decimal("2.0"),
    })

    r2 = engine.screen({
        "B": Decimal("2.0"),
        "A": Decimal("1.0"),
    })

    assert r1.state_hash == r2.state_hash