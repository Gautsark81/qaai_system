from core.strategy_factory.governance.promotion_readiness import (
    evaluate_promotion_readiness,
)


def test_strategy_promotion_readiness_passes():
    """
    A strategy is promotion-ready if:
    - SSR >= 0.6
    - Drawdown not breached
    - Minimum trades satisfied
    """

    metrics = {
        "ssr": 0.7,
        "trade_count": 20,
        "drawdown_breached": False,
    }

    result = evaluate_promotion_readiness(metrics)

    assert result.is_eligible is True
    assert "eligible" in result.reason.lower()
