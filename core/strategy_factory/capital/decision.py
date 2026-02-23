from __future__ import annotations

from core.strategy_factory.lifecycle.contracts import StrategyLifecycleState
from core.strategy_factory.promotion.models import PromotionLevel
from core.strategy_factory.health.models import StrategyHealthSnapshot
from core.strategy_factory.capital.models import CapitalEligibilityDecision


def decide_capital_eligibility(
    *,
    lifecycle_state: StrategyLifecycleState,
    promotion_level: PromotionLevel,
    health: StrategyHealthSnapshot,
) -> CapitalEligibilityDecision:
    """
    Decide whether a strategy is eligible to receive capital.

    Governance-only decision:
    - No sizing
    - No execution
    - No time
    - No side effects
    """

    # --------------------------------------------------
    # 1️⃣ Lifecycle gate
    # --------------------------------------------------
    if lifecycle_state != StrategyLifecycleState.LIVE:
        return CapitalEligibilityDecision(
            eligible=False,
            reason="Strategy lifecycle state is not LIVE",
        )

    # --------------------------------------------------
    # 2️⃣ Promotion gate
    # --------------------------------------------------
    if promotion_level != PromotionLevel.LIVE_ELIGIBLE:
        return CapitalEligibilityDecision(
            eligible=False,
            reason="Strategy promotion level is not LIVE_ELIGIBLE",
        )

    # --------------------------------------------------
    # 3️⃣ Health gate — SSR
    # --------------------------------------------------
    if health.ssr < 0.80:
        return CapitalEligibilityDecision(
            eligible=False,
            reason="Strategy SSR below capital eligibility threshold",
        )

    # --------------------------------------------------
    # 4️⃣ Health gate — Drawdown
    # --------------------------------------------------
    if health.max_drawdown > 0.20:
        return CapitalEligibilityDecision(
            eligible=False,
            reason="Strategy drawdown exceeds capital eligibility limit",
        )

    # --------------------------------------------------
    # ✅ Eligible
    # --------------------------------------------------
    return CapitalEligibilityDecision(
        eligible=True,
        reason="Strategy eligible for capital allocation",
    )
