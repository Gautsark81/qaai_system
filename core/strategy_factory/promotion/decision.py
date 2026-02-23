from __future__ import annotations

from typing import Optional

from core.strategy_factory.health.models import StrategyHealthSnapshot
from core.strategy_factory.promotion.models import (
    PromotionDecision,
    PromotionLevel,
    PromotionPolicy,
)
from core.strategy_factory.promotion.paper import PaperTradeSnapshot
from core.strategy_factory.promotion.memory import PromotionMemory


def decide_promotion(
    snapshot: StrategyHealthSnapshot,
    policy: PromotionPolicy,
    paper_snapshot: Optional[PaperTradeSnapshot] = None,
    memory: Optional[PromotionMemory] = None,
) -> PromotionDecision:
    """
    Decide the promotion level for a strategy based on:
    - Health evidence
    - Paper-trade confirmation (C1.4-B)
    - Promotion memory (cooldown / downgrade stickiness)

    Backward-compatible with C1.4-A positional calls.
    Pure, deterministic, governance-only.
    """

    # --------------------------------------------------
    # 1️⃣ Hard drawdown violation (absolute)
    # --------------------------------------------------
    if snapshot.max_drawdown > policy.max_drawdown:
        return PromotionDecision(
            level=PromotionLevel.REJECTED,
            reason="Rejected due to drawdown exceeding policy limit",
        )

    # --------------------------------------------------
    # 2️⃣ Insufficient samples (downgrade only)
    # --------------------------------------------------
    if snapshot.total_trades < policy.min_samples:
        return PromotionDecision(
            level=PromotionLevel.RESEARCH,
            reason="Downgraded due to insufficient samples",
        )

    # --------------------------------------------------
    # 3️⃣ Base SSR-based promotion (C1.4-A)
    # --------------------------------------------------
    ssr = snapshot.ssr

    if ssr < policy.research_ssr:
        base_level = PromotionLevel.REJECTED
        base_reason = "SSR below research threshold"

    elif ssr < policy.paper_ssr:
        base_level = PromotionLevel.RESEARCH
        base_reason = "SSR qualifies for research tier"

    elif ssr < policy.live_ssr:
        base_level = PromotionLevel.PAPER
        base_reason = "SSR qualifies for paper trading"

    else:
        base_level = PromotionLevel.LIVE_ELIGIBLE
        base_reason = "SSR qualifies for live eligibility"

    # --------------------------------------------------
    # 4️⃣ Paper confirmation for LIVE_ELIGIBLE (C1.4-B)
    # --------------------------------------------------
    if base_level == PromotionLevel.LIVE_ELIGIBLE:
        paper_required = (
            policy.paper_confirm_ssr > 0.0
            or policy.paper_max_drawdown < 1.0
        )

        if paper_required:
            if paper_snapshot is None:
                return PromotionDecision(
                    level=PromotionLevel.PAPER,
                    reason="paper confirmation required for live eligibility",
                )

            if paper_snapshot.paper_ssr < policy.paper_confirm_ssr:
                return PromotionDecision(
                    level=PromotionLevel.PAPER,
                    reason="paper ssr below live confirmation threshold",
                )

            if paper_snapshot.paper_drawdown > policy.paper_max_drawdown:
                return PromotionDecision(
                    level=PromotionLevel.PAPER,
                    reason="paper drawdown exceeds policy limit",
                )

    # --------------------------------------------------
    # 5️⃣ Promotion memory cooldown (downgrade dominance)
    # --------------------------------------------------
    if (
        memory is not None
        and memory.downgrade_count > 0
        and base_level == PromotionLevel.LIVE_ELIGIBLE
        and memory.last_level != PromotionLevel.LIVE_ELIGIBLE
    ):
        return PromotionDecision(
            level=PromotionLevel.PAPER,
            reason="upgrade blocked due to recent downgrade cooldown",
        )

    # --------------------------------------------------
    # 6️⃣ Final decision
    # --------------------------------------------------
    return PromotionDecision(
        level=base_level,
        reason=base_reason,
    )
