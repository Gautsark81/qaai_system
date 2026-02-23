from decimal import Decimal

from core.strategy_factory.screening.screening_engine import ScreeningEngine
from core.strategy_factory.screening.regime_overlay import RegimeScoringOverlay


def test_overlay_order_independent():
    engine = ScreeningEngine()
    overlay = RegimeScoringOverlay()

    base = engine.screen({
        "A": Decimal("1.0"),
        "B": Decimal("2.0"),
    })

    weights_1 = {"A": Decimal("2.0")}
    weights_2 = {"A": Decimal("2.0")}

    r1 = overlay.apply(base, "BULL", weights_1)
    r2 = overlay.apply(base, "BULL", weights_2)

    assert r1.state_hash == r2.state_hash