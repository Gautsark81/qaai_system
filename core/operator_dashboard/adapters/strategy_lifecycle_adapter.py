from typing import List, Optional

from core.operator_dashboard.contracts.strategy_lifecycle import (
    StrategyLifecycleView,
)
from core.strategy.strategy_registry import StrategyRegistry
from core.tournament.promotion_store import PromotionStore
from core.tournament.paper_store import PaperEvaluationStore
from core.tournament.live_candidate_store import LiveCandidateStore
from core.tournament.live_governance_store import LiveGovernanceStore
from core.safety.kill_switch import KillSwitch


def load_strategy_lifecycle_views() -> List[StrategyLifecycleView]:
    """
    Central lifecycle join across:
    - Strategy registry
    - Promotion artifacts
    - Paper evaluation
    - Live candidates
    - Governance decisions

    This adapter is intentionally READ-ONLY and deterministic.
    It must never infer state that cannot be explained.
    """

    registry = StrategyRegistry()
    promotions = PromotionStore()
    paper_store = PaperEvaluationStore()
    live_candidates = LiveCandidateStore()
    live_governance = LiveGovernanceStore()

    kill_switch = KillSwitch(scope="global")

    strategies = registry.list_all()
    views: List[StrategyLifecycleView] = []

    for strat in strategies:
        strategy_id = strat.strategy_id

        # -------------------------------------------------
        # Defaults (safe, conservative)
        # -------------------------------------------------
        lifecycle_stage = "generated"
        status = "allowed"

        backtest_ssr: Optional[float] = None
        paper_ssr: Optional[float] = None

        last_decision: Optional[str] = None
        last_reason: Optional[str] = None

        approval_stage: Optional[str] = None
        approval_status: Optional[str] = None

        risk_flags: List[str] = []

        # -------------------------------------------------
        # Promotion → Backtest gate
        # -------------------------------------------------
        promo = promotions.latest_for_strategy(strategy_id)
        if promo:
            lifecycle_stage = "backtested"
            last_decision = "backtest_gate"
            last_reason = ",".join(promo.get("reasons") or [])

            if not promo.get("promoted", False):
                status = "blocked"
                risk_flags.append("BACKTEST_REJECTED")

        # -------------------------------------------------
        # Paper Evaluation
        # -------------------------------------------------
        paper = paper_store.latest_for_strategy(strategy_id)
        if paper:
            lifecycle_stage = "paper"
            paper_ssr = paper.get("paper_ssr")

            if paper_ssr is not None and paper_ssr < 0.8:
                risk_flags.append("PAPER_SSR_WEAK")

        # -------------------------------------------------
        # Live Candidate
        # -------------------------------------------------
        live = live_candidates.latest_for_strategy(strategy_id)
        if live:
            lifecycle_stage = "live_candidate"

            if live.get("blocked"):
                status = "blocked"
                risk_flags.append("LIVE_CANDIDATE_BLOCKED")

        # -------------------------------------------------
        # Live Governance (Human-in-the-loop)
        # -------------------------------------------------
        gov = live_governance.latest_for_strategy(strategy_id)
        if gov:
            approval_stage = "live"
            approval_status = gov.get("status")

            if approval_status != "approved":
                status = "pending_approval"
                risk_flags.append("GOVERNANCE_PENDING")

            last_decision = "live_governance"
            last_reason = gov.get("reason")

        # -------------------------------------------------
        # Global Kill Switch
        # -------------------------------------------------
        if kill_switch.is_armed():
            status = "halted"
            risk_flags.append("KILL_SWITCH_ACTIVE")

        # -------------------------------------------------
        # Assemble View
        # -------------------------------------------------
        views.append(
            StrategyLifecycleView(
                strategy_id=strategy_id,
                version=strat.version,

                lifecycle_stage=lifecycle_stage,
                status=status,

                backtest_ssr=backtest_ssr,
                paper_ssr=paper_ssr,

                last_decision=last_decision,
                last_decision_reason=last_reason,

                human_approval_stage=approval_stage,
                human_approval_status=approval_status,

                risk_flags=sorted(set(risk_flags)),
                kill_switch_active=kill_switch.is_armed(),
            )
        )

    return views
