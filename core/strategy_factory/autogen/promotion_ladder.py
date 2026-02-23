# core/strategy_factory/autogen/promotion_ladder.py

from .candidate_registry import CandidateRegistry
from .candidate_models import CandidateStage


MIN_SHADOW_CYCLES = 30
MIN_PAPER_SSR = 75.0
MIN_LIVE_SSR = 80.0


class PromotionLadder:

    def __init__(self, registry: CandidateRegistry):
        self.registry = registry

    # --------------------------------------------------
    # ROBUST_VALIDATED → PAPER
    # --------------------------------------------------
    def promote_to_paper(self, hypothesis_id: str):

        latest = self.registry.get_latest(hypothesis_id)

        if latest is None:
            raise ValueError("Candidate not found")

        if latest.stage != CandidateStage.ROBUST_VALIDATED:
            raise ValueError("Must be ROBUST_VALIDATED before PAPER")

        return self.registry.update_stage(
            hypothesis_id,
            CandidateStage.PAPER,
            ssr=latest.ssr,
            max_drawdown=latest.max_drawdown,
        )

    # --------------------------------------------------
    # PAPER → SHADOW
    # --------------------------------------------------
    def promote_to_shadow(self, hypothesis_id: str):

        latest = self.registry.get_latest(hypothesis_id)

        if latest.stage != CandidateStage.PAPER:
            raise ValueError("Must be PAPER before SHADOW")

        if latest.ssr is None or latest.ssr < MIN_PAPER_SSR:
            raise ValueError("SSR below minimum for SHADOW")

        if latest.shadow_cycles < MIN_SHADOW_CYCLES:
            raise ValueError("Insufficient shadow cycles")

        return self.registry.update_stage(
            hypothesis_id,
            CandidateStage.SHADOW,
            ssr=latest.ssr,
            max_drawdown=latest.max_drawdown,
            shadow_cycles=latest.shadow_cycles,
        )

    # --------------------------------------------------
    # SHADOW → LIVE_ELIGIBLE
    # --------------------------------------------------
    def promote_to_live_eligible(self, hypothesis_id: str):

        latest = self.registry.get_latest(hypothesis_id)

        if latest.stage != CandidateStage.SHADOW:
            raise ValueError("Must be SHADOW before LIVE_ELIGIBLE")

        if latest.ssr is None or latest.ssr < MIN_LIVE_SSR:
            raise ValueError("SSR below minimum for LIVE")

        return self.registry.update_stage(
            hypothesis_id,
            CandidateStage.LIVE_ELIGIBLE,
            ssr=latest.ssr,
            max_drawdown=latest.max_drawdown,
            shadow_cycles=latest.shadow_cycles,
        )

    # --------------------------------------------------
    # LIVE_ELIGIBLE → LIVE
    # Governance-gated (explicit call required)
    # --------------------------------------------------
    def promote_to_live(self, hypothesis_id: str, governance_approved: bool):

        latest = self.registry.get_latest(hypothesis_id)

        if latest.stage != CandidateStage.LIVE_ELIGIBLE:
            raise ValueError("Must be LIVE_ELIGIBLE before LIVE")

        if not governance_approved:
            raise ValueError("Governance approval required")

        return self.registry.update_stage(
            hypothesis_id,
            CandidateStage.LIVE,
            ssr=latest.ssr,
            max_drawdown=latest.max_drawdown,
            shadow_cycles=latest.shadow_cycles,
        )

    # --------------------------------------------------
    # Retirement (Allowed from any non-LIVE stage)
    # --------------------------------------------------
    def retire(self, hypothesis_id: str):

        latest = self.registry.get_latest(hypothesis_id)

        if latest is None:
            raise ValueError("Candidate not found")

        if latest.stage == CandidateStage.LIVE:
            raise ValueError("LIVE strategy requires manual governance removal")

        return self.registry.update_stage(
            hypothesis_id,
            CandidateStage.RETIRED,
            ssr=latest.ssr,
            max_drawdown=latest.max_drawdown,
            shadow_cycles=latest.shadow_cycles,
        )