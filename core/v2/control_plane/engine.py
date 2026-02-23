from __future__ import annotations
from core.v2.control_plane.decisions import PromotionDecision
from core.v2.control_plane.permissions import PromotionPermissions
from core.v2.simulation.lifecycle_simulator import LifecycleSimulator
from core.v2.simulation.exposure_simulator import ExposureSimulator
from core.v2.intelligence.strategy_scoring import AlphaScore
from .kill_matrix import evaluate_kill_matrix
from .contracts import KillDecision, KillSignal


class PromotionEngine:
    """
    Final authority for strategy promotion.
    """

    MIN_STRONG_ALPHA = 0.75
    MIN_MODERATE_ALPHA = 0.6
    MIN_SSR = 0.80

    def evaluate(
        self,
        *,
        alpha: AlphaScore,
        ssr: float,
        lifecycle_outcome,
        exposure_safe: bool,
    ) -> PromotionPermissions:

        # --------------------------------
        # HARD STOPS
        # --------------------------------
        if lifecycle_outcome.decision == "KILL":
            return PromotionPermissions(False, False, "Lifecycle kill")

        if not exposure_safe:
            return PromotionPermissions(False, False, "Exposure risk")

        # --------------------------------
        # SSR IS NON-NEGOTIABLE
        # --------------------------------
        if ssr < self.MIN_SSR:
            return PromotionPermissions(False, True, "SSR below threshold")

        # --------------------------------
        # ALPHA GOVERNANCE
        # --------------------------------
        if alpha.score >= self.MIN_STRONG_ALPHA:
            return PromotionPermissions(True, True, "Strong alpha")

        if alpha.score >= self.MIN_MODERATE_ALPHA:
            return PromotionPermissions(False, True, "Moderate alpha")

        return PromotionPermissions(False, False, "Weak alpha")

    def apply_kill_switches(
        self,
        *,
        kill_signals: list[KillSignal],
    ) -> KillDecision:
        return evaluate_kill_matrix(kill_signals)