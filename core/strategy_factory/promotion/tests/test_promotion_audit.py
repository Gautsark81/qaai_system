from datetime import datetime

from core.strategy_factory.health.models import StrategyHealthSnapshot
from core.strategy_factory.promotion.models import (
    PromotionDecision,
    PromotionLevel,
    PromotionPolicy,
)
from core.strategy_factory.promotion.paper import PaperTradeSnapshot
from core.strategy_factory.promotion.memory import PromotionMemory
from core.strategy_factory.promotion.audit import build_promotion_audit


def make_health():
    return StrategyHealthSnapshot(
        strategy_dna="STRAT-001",
        ssr=0.85,
        total_trades=500,
        max_drawdown=0.05,
        decay_risk=0.1,
        flags=[],
    )


def make_policy():
    return PromotionPolicy(
        min_samples=100,
        research_ssr=0.55,
        paper_ssr=0.65,
        live_ssr=0.80,
        paper_confirm_ssr=0.75,
        paper_max_drawdown=0.10,
        max_drawdown=0.20,
    )


def test_audit_record_is_deterministic():
    ts = datetime(2025, 1, 1)

    decision = PromotionDecision(
        level=PromotionLevel.LIVE_ELIGIBLE,
        reason="ssr qualifies",
    )

    audit1 = build_promotion_audit(
        snapshot=make_health(),
        policy=make_policy(),
        decision=decision,
        paper_snapshot=None,
        memory=None,
        created_at=ts,
    )

    audit2 = build_promotion_audit(
        snapshot=make_health(),
        policy=make_policy(),
        decision=decision,
        paper_snapshot=None,
        memory=None,
        created_at=ts,
    )

    assert audit1 == audit2


def test_audit_fingerprints_present():
    ts = datetime(2025, 1, 1)

    audit = build_promotion_audit(
        snapshot=make_health(),
        policy=make_policy(),
        decision=PromotionDecision(
            level=PromotionLevel.PAPER,
            reason="paper confirmation required",
        ),
        paper_snapshot=PaperTradeSnapshot(
            paper_ssr=0.70,
            paper_trades=200,
            paper_drawdown=0.06,
            flags=[],
        ),
        memory=PromotionMemory(
            last_level=PromotionLevel.RESEARCH,
            last_decision_at=None,
            downgrade_count=1,
        ),
        created_at=ts,
    )

    assert audit.health_fingerprint
    assert audit.policy_fingerprint
    assert audit.paper_fingerprint
    assert audit.memory_fingerprint
