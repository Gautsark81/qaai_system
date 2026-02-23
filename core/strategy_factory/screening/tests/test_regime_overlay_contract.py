from decimal import Decimal

from core.strategy_factory.screening.screening_engine import ScreeningEngine
from core.strategy_factory.screening.regime_overlay import RegimeScoringOverlay


def test_overlay_contract_structure():
    engine = ScreeningEngine()
    overlay = RegimeScoringOverlay()

    base = engine.screen({
        "A": Decimal("1.0"),
        "B": Decimal("2.0"),
    })

    result = overlay.apply(
        base,
        regime="BULL",
        regime_weights={"A": Decimal("2.0")},
    )

    assert len(result.scores) == 2
    assert result.state_hash is not None