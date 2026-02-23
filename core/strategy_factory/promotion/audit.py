from __future__ import annotations

from datetime import datetime
from typing import Optional

from core.strategy_factory.health.models import StrategyHealthSnapshot
from core.strategy_factory.promotion.models import (
    PromotionAuditRecord,
    PromotionDecision,
    PromotionPolicy,
)
from core.strategy_factory.promotion.paper import PaperTradeSnapshot
from core.strategy_factory.promotion.memory import PromotionMemory
from core.strategy_factory.promotion.fingerprints import fingerprint


def build_promotion_audit(
    *,
    snapshot: StrategyHealthSnapshot,
    policy: PromotionPolicy,
    decision: PromotionDecision,
    paper_snapshot: Optional[PaperTradeSnapshot],
    memory: Optional[PromotionMemory],
    created_at: datetime,
) -> PromotionAuditRecord:
    """
    Build an immutable audit record for a promotion decision.

    Pure, deterministic, and behavior-preserving.
    """

    return PromotionAuditRecord(
        strategy_dna=snapshot.strategy_dna,
        decision=decision,
        health_fingerprint=fingerprint(snapshot),
        policy_fingerprint=fingerprint(policy),
        paper_fingerprint=fingerprint(paper_snapshot) if paper_snapshot else None,
        memory_fingerprint=fingerprint(memory) if memory else None,
        created_at=created_at,
    )
