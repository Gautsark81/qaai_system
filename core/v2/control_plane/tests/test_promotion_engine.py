from core.v2.control_plane.engine import PromotionEngine
from core.v2.intelligence.strategy_scoring import AlphaScore


class DummyLifecycle:
    def __init__(self, decision):
        self.decision = decision


def test_strong_alpha_promotion():
    engine = PromotionEngine()

    alpha = AlphaScore(
        strategy_id="S1",
        alpha_score=0.85,
        verdict="STRONG_ALPHA",
        ssr=0.9,
        health=0.9,
        regime_fit=0.9,
        stability=0.8,
        components={},
    )

    perms = engine.evaluate(
        alpha=alpha,
        ssr=0.9,
        lifecycle_outcome=DummyLifecycle("CONTINUE"),
        exposure_safe=True,
    )

    assert perms.allow_live is True
