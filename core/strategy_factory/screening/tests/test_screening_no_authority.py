from decimal import Decimal

from core.strategy_factory.screening.screening_engine import ScreeningEngine


def test_screening_has_no_authority_methods():
    engine = ScreeningEngine()

    forbidden = [
        "allocate",
        "promote",
        "execute",
        "mutate",
        "approve",
    ]

    for method in forbidden:
        assert not hasattr(engine, method)