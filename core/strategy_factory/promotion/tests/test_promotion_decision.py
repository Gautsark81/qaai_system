import pytest

from core.strategy_factory.health.models import StrategyHealthSnapshot
from core.strategy_factory.promotion.models import (
    PromotionLevel,
    PromotionPolicy,
)
from core.strategy_factory.promotion.decision import decide_promotion


def make_snapshot(ssr: float, samples: int = 200, drawdown: float = 0.05):
    return StrategyHealthSnapshot(
        ssr=ssr,
        total_trades=samples,
        max_drawdown=drawdown,
        decay_risk=0.1,
        flags=[],
    )


def test_reject_when_ssr_below_research_threshold():
    policy = PromotionPolicy(
        min_samples=100,
        research_ssr=0.55,
        paper_ssr=0.65,
        live_ssr=0.80,
        max_drawdown=0.20,
    )

    snapshot = make_snapshot(ssr=0.40)

    decision = decide_promotion(snapshot, policy)

    assert decision.level == PromotionLevel.REJECTED
    assert "SSR below research threshold" in decision.reason


def test_research_when_ssr_between_research_and_paper():
    policy = PromotionPolicy(
        min_samples=100,
        research_ssr=0.55,
        paper_ssr=0.65,
        live_ssr=0.80,
        max_drawdown=0.20,
    )

    snapshot = make_snapshot(ssr=0.60)

    decision = decide_promotion(snapshot, policy)

    assert decision.level == PromotionLevel.RESEARCH


def test_paper_when_ssr_above_paper_threshold():
    policy = PromotionPolicy(
        min_samples=100,
        research_ssr=0.55,
        paper_ssr=0.65,
        live_ssr=0.80,
        max_drawdown=0.20,
    )

    snapshot = make_snapshot(ssr=0.70)

    decision = decide_promotion(snapshot, policy)

    assert decision.level == PromotionLevel.PAPER


def test_live_eligible_when_ssr_above_live_threshold():
    policy = PromotionPolicy(
        min_samples=100,
        research_ssr=0.55,
        paper_ssr=0.65,
        live_ssr=0.80,
        max_drawdown=0.20,
    )

    snapshot = make_snapshot(ssr=0.85)

    decision = decide_promotion(snapshot, policy)

    assert decision.level == PromotionLevel.LIVE_ELIGIBLE


def test_insufficient_samples_forces_downgrade():
    policy = PromotionPolicy(
        min_samples=100,
        research_ssr=0.55,
        paper_ssr=0.65,
        live_ssr=0.80,
        max_drawdown=0.20,
    )

    snapshot = make_snapshot(ssr=0.90, samples=20)

    decision = decide_promotion(snapshot, policy)

    assert decision.level == PromotionLevel.RESEARCH
    assert "insufficient samples" in decision.reason


def test_excess_drawdown_forces_rejection():
    policy = PromotionPolicy(
        min_samples=100,
        research_ssr=0.55,
        paper_ssr=0.65,
        live_ssr=0.80,
        max_drawdown=0.10,
    )

    snapshot = make_snapshot(ssr=0.90, drawdown=0.25)

    decision = decide_promotion(snapshot, policy)

    assert decision.level == PromotionLevel.REJECTED
    assert "drawdown" in decision.reason
