from core.live_ops.promotion import PromotionRequest
from core.live_ops.enums import PromotionDecision, StrategyStage


def test_promotion_request_contract():
    req = PromotionRequest(
        strategy_id="breakout_v3",
        from_stage=StrategyStage.PAPER_APPROVED,
        to_stage=StrategyStage.LIVE_APPROVED,
        decision=PromotionDecision.PROMOTE,
        reason="SSR stable above 0.85 for 30 days",
    )

    assert req.strategy_id
    assert req.from_stage != req.to_stage
    assert req.decision == PromotionDecision.PROMOTE
    assert isinstance(req.reason, str)
