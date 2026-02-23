from datetime import datetime

from core.strategy_factory.health.models import StrategyHealthSnapshot
from core.strategy_factory.promotion.models import (
    PromotionLevel,
    PromotionPolicy,
)
from core.strategy_factory.promotion.decision import decide_promotion
from core.strategy_factory.promotion.paper import PaperTradeSnapshot
from core.strategy_factory.promotion.memory import PromotionMemory


def make_health(ssr: float):
    return StrategyHealthSnapshot(
        ssr=ssr,
        total_trades=500,
        max_drawdown=0.05,
        decay_risk=0.1,
        flags=[],
    )


def make_paper(ssr: float):
    return PaperTradeSnapshot(
        paper_ssr=ssr,
        paper_trades=200,
        paper_drawdown=0.04,
        flags=[],
    )


def test_live_requires_paper_confirmation():
    policy = PromotionPolicy(
        min_samples=100,
        research_ssr=0.55,
        paper_ssr=0.65,
        live_ssr=0.80,
        paper_confirm_ssr=0.75,
        max_drawdown=0.20,
        paper_max_drawdown=0.10,
    )

    decision = decide_promotion(
        snapshot=make_health(ssr=0.85),
        policy=policy,
        paper_snapshot=None,
        memory=None,
    )

    assert decision.level == PromotionLevel.PAPER
    assert "paper confirmation required" in decision.reason


def test_live_confirmed_with_strong_paper():
    policy = PromotionPolicy(
        min_samples=100,
        research_ssr=0.55,
        paper_ssr=0.65,
        live_ssr=0.80,
        paper_confirm_ssr=0.75,
        max_drawdown=0.20,
        paper_max_drawdown=0.10,
    )

    decision = decide_promotion(
        snapshot=make_health(ssr=0.90),
        policy=policy,
        paper_snapshot=make_paper(ssr=0.80),
        memory=None,
    )

    assert decision.level == PromotionLevel.LIVE_ELIGIBLE


def test_previous_downgrade_blocks_immediate_upgrade():
    policy = PromotionPolicy(
        min_samples=100,
        research_ssr=0.55,
        paper_ssr=0.65,
        live_ssr=0.80,
        paper_confirm_ssr=0.75,
        max_drawdown=0.20,
        paper_max_drawdown=0.10,
    )

    memory = PromotionMemory(
        last_level=PromotionLevel.PAPER,
        last_decision_at=datetime.utcnow(),
        downgrade_count=1,
    )

    decision = decide_promotion(
        snapshot=make_health(ssr=0.95),
        policy=policy,
        paper_snapshot=make_paper(ssr=0.90),
        memory=memory,
    )

    assert decision.level == PromotionLevel.PAPER
    assert "cooldown" in decision.reason
