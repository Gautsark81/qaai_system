import uuid
from typing import List

from modules.strategy_health.healing_actions import HealingAction
from modules.strategy_health.healing_result import HealingResult
from modules.strategy_health.decay_detector import DecaySignal
from modules.strategy_health.state_machine import StrategyState
from modules.strategy_health.telemetry import StrategyTelemetry


# ==========================================================
# SELF-HEALING ORCHESTRATOR
# ==========================================================

class SelfHealingOrchestrator:
    """
    Offline-only self-healing engine.

    Produces candidate strategies for re-evaluation.
    NEVER touches live instances.
    """

    def __init__(
        self,
        *,
        max_attempts: int = 3,
    ):
        self.max_attempts = max_attempts

    # ------------------------------------------------------
    # PUBLIC API
    # ------------------------------------------------------

    def heal(
        self,
        *,
        strategy_id: str,
        state: StrategyState,
        decay_signal: DecaySignal,
        telemetry: StrategyTelemetry,
    ) -> HealingResult:
        """
        Attempts to heal a decaying strategy.

        Returns a NEW strategy id if successful.
        """

        # -------------------------
        # Eligibility gate
        # -------------------------
        if state != StrategyState.PAUSED:
            return HealingResult(
                success=False,
                new_strategy_id=None,
                reason="Strategy not paused; healing not allowed",
            )

        if decay_signal.level != "STRUCTURAL_DECAY":
            return HealingResult(
                success=False,
                new_strategy_id=None,
                reason="Decay not structural; healing not required",
            )

        # -------------------------
        # Generate healing plan
        # -------------------------
        actions = self._generate_actions(telemetry)

        # -------------------------
        # Execute bounded attempts
        # -------------------------
        for idx, action in enumerate(actions[: self.max_attempts]):
            candidate_id = self._spawn_candidate(strategy_id, idx)

            # NOTE: Actual backtest / validation is OUTSIDE this module
            # This module only proposes candidates

            return HealingResult(
                success=True,
                new_strategy_id=candidate_id,
                reason=f"Healing action applied: {action.action_type}",
            )

        # -------------------------
        # Failure → retire
        # -------------------------
        return HealingResult(
            success=False,
            new_strategy_id=None,
            reason="All healing attempts exhausted; strategy should be retired",
        )

    # ------------------------------------------------------
    # INTERNALS
    # ------------------------------------------------------

    def _generate_actions(
        self,
        telemetry: StrategyTelemetry,
    ) -> List[HealingAction]:
        """
        Ranked, bounded healing actions.
        """

        actions: List[HealingAction] = []

        # 1️⃣ Parameter tightening
        actions.append(
            HealingAction(
                action_type="PARAM_TIGHTEN",
                parameters={"risk_multiplier": 0.8},
                reason="Reduce drawdown exposure",
            )
        )

        # 2️⃣ Feature pruning
        actions.append(
            HealingAction(
                action_type="FEATURE_PRUNE",
                parameters={"remove_weakest": True},
                reason="Remove unstable signals",
            )
        )

        # 3️⃣ Regime realignment
        actions.append(
            HealingAction(
                action_type="REGIME_REALIGN",
                parameters={"volatility_bucket": "LOW"},
                reason="Mismatch with volatility regime",
            )
        )

        return actions

    def _spawn_candidate(self, parent_id: str, attempt: int) -> str:
        """
        Creates a new immutable candidate id.
        """
        return f"{parent_id}_heal_{attempt}_{uuid.uuid4().hex[:8]}"
