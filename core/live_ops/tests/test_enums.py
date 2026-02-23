import pytest

from core.live_ops.enums import (
    TradingMode,
    StrategyStage,
    PromotionDecision,
)


def test_trading_mode_enum():
    assert TradingMode.BACKTEST.value == "BACKTEST"
    assert TradingMode.PAPER.value == "PAPER"
    assert TradingMode.LIVE.value == "LIVE"


def test_strategy_stage_enum():
    assert StrategyStage.GENERATED.value == "GENERATED"
    assert StrategyStage.PAPER_APPROVED.value == "PAPER_APPROVED"
    assert StrategyStage.LIVE_APPROVED.value == "LIVE_APPROVED"
    assert StrategyStage.REJECTED.value == "REJECTED"


def test_promotion_decision_enum():
    assert PromotionDecision.PROMOTE.value == "PROMOTE"
    assert PromotionDecision.HOLD.value == "HOLD"
    assert PromotionDecision.REJECT.value == "REJECT"
