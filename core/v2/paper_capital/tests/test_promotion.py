from core.v2.paper_capital.promotion import (
    PromotionGate,
    PromotionInput,
)


def test_promotion_success():
    gate = PromotionGate(min_ssr=0.8, max_stability_stddev=0.5)

    inputs = [
        PromotionInput(
            strategy_id="a",
            ssr=0.9,
            stability_stddev=0.2,
            regime_match=True,
        )
    ]

    decisions = gate.evaluate(inputs)

    assert decisions[0].promoted is True
    assert "SSR>=0.8" in decisions[0].reasons


def test_promotion_fails_on_low_ssr():
    gate = PromotionGate(min_ssr=0.8)

    inputs = [
        PromotionInput(
            strategy_id="b",
            ssr=0.6,
            stability_stddev=0.1,
            regime_match=True,
        )
    ]

    decisions = gate.evaluate(inputs)

    assert decisions[0].promoted is False
    assert "SSR<0.8" in decisions[0].reasons


def test_promotion_fails_on_stability():
    gate = PromotionGate(max_stability_stddev=0.3)

    inputs = [
        PromotionInput(
            strategy_id="c",
            ssr=0.95,
            stability_stddev=0.6,
            regime_match=True,
        )
    ]

    decisions = gate.evaluate(inputs)

    assert decisions[0].promoted is False
    assert "stability>0.3" in decisions[0].reasons


def test_promotion_fails_on_regime_mismatch():
    gate = PromotionGate()

    inputs = [
        PromotionInput(
            strategy_id="d",
            ssr=0.95,
            stability_stddev=0.1,
            regime_match=False,
        )
    ]

    decisions = gate.evaluate(inputs)

    assert decisions[0].promoted is False
    assert "regime_mismatch" in decisions[0].reasons
