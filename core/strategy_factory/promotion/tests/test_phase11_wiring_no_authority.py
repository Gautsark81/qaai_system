from core.strategy_factory.promotion.wiring.shadow_to_paper_wiring import (
    ShadowToPaperWiringEvaluator,
)


def test_shadow_to_paper_wiring_has_no_side_effects():
    evaluator = ShadowToPaperWiringEvaluator()

    forbidden = [
        "execute",
        "place_order",
        "allocate",
        "arm",
        "broker",
        "capital",
    ]

    for attr in forbidden:
        assert not hasattr(evaluator, attr)
