from core.strategy_factory.screening.regime_overlay import RegimeScoringOverlay


def test_overlay_has_no_authority():
    overlay = RegimeScoringOverlay()

    forbidden = [
        "allocate",
        "promote",
        "execute",
        "approve",
        "mutate",
    ]

    for method in forbidden:
        assert not hasattr(overlay, method)