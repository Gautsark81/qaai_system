# modules/strategy_health/state_machine.py

from enum import Enum
from dataclasses import dataclass
from typing import Optional

from modules.strategy_health.evaluator import HealthResult
from modules.strategy_health.decay_detector import DecaySignal


# ==========================================================
# Strategy States
# ==========================================================

class StrategyState(Enum):
    ACTIVE = "ACTIVE"
    WARNING = "WARNING"
    DEGRADED = "DEGRADED"
    PAUSED = "PAUSED"
    RETIRED = "RETIRED"


# ==========================================================
# State Memory
# ==========================================================

@dataclass
class StateMemory:
    consecutive_warning: int = 0
    consecutive_degraded: int = 0
    consecutive_recovery: int = 0


# ==========================================================
# Transition Result
# ==========================================================

@dataclass
class StateTransition:
    from_state: StrategyState
    to_state: StrategyState
    reason: str


# ==========================================================
# Strategy State Machine
# ==========================================================

class StrategyStateMachine:
    """
    Deterministic strategy state machine.

    Wiring rules:
    - DecayDetector is read-only
    - Only STRUCTURAL_DECAY may escalate to PAUSED
    - INSUFFICIENT_TRADES blocks ALL transitions
    """

    def __init__(self, *, retirement_days: int = 30):
        self.retirement_days = retirement_days

    def step(
        self,
        *,
        current_state: StrategyState,
        health_result: HealthResult,
        memory: StateMemory,
        decay_signal: Optional[DecaySignal] = None,
    ) -> Optional[StateTransition]:

        flags = set(health_result.flags)
        health = health_result.health_score
        win_rate_score = health_result.signals.get("win_rate", 0.0)

        # ==================================================
        # 1️⃣ INSUFFICIENT DATA — ABSOLUTE BLOCK
        # ==================================================
        if "INSUFFICIENT_TRADES" in flags:
            return None

        # ==================================================
        # 2️⃣ STRUCTURAL DECAY ESCALATION (C2.3 → C2.2)
        # ==================================================
        if (
            decay_signal
            and decay_signal.level == "STRUCTURAL_DECAY"
            and current_state != StrategyState.PAUSED
        ):
            return StateTransition(
                from_state=current_state,
                to_state=StrategyState.PAUSED,
                reason="Structural decay confirmed across multiple windows",
            )

        # ==================================================
        # 3️⃣ HARD SAFETY OVERRIDES
        # ==================================================
        if (
            "DRAWDOWN_RISK" in flags
            or "WIN_RATE_INVALID" in flags
            or health < 0.40
        ):
            if current_state != StrategyState.PAUSED:
                return StateTransition(
                    from_state=current_state,
                    to_state=StrategyState.PAUSED,
                    reason="Critical drawdown, invalid win rate, or health < 0.40",
                )
            return None

        # ==================================================
        # 4️⃣ SOFT DECAY (PERSISTENCE)
        # ==================================================

        if win_rate_score < 1.0:
            memory.consecutive_warning += 1
        else:
            memory.consecutive_warning = 0

        if win_rate_score < 0.6:
            memory.consecutive_degraded += 1
        else:
            memory.consecutive_degraded = 0

        if (
            current_state == StrategyState.ACTIVE
            and memory.consecutive_warning >= 2
        ):
            return StateTransition(
                from_state=StrategyState.ACTIVE,
                to_state=StrategyState.WARNING,
                reason="Win rate below 80% for two consecutive evaluations",
            )

        if (
            current_state == StrategyState.WARNING
            and memory.consecutive_degraded >= 2
        ):
            return StateTransition(
                from_state=StrategyState.WARNING,
                to_state=StrategyState.DEGRADED,
                reason="Persistent win rate decay below 70%",
            )

        if (
            current_state == StrategyState.DEGRADED
            and health < 0.55
        ):
            return StateTransition(
                from_state=StrategyState.DEGRADED,
                to_state=StrategyState.PAUSED,
                reason="Health below degraded threshold (0.55)",
            )

        # ==================================================
        # 5️⃣ RECOVERY
        # ==================================================

        if health >= 0.75 and win_rate_score == 1.0:
            memory.consecutive_recovery += 1
        else:
            memory.consecutive_recovery = 0

        if (
            current_state == StrategyState.DEGRADED
            and memory.consecutive_recovery >= 3
        ):
            return StateTransition(
                from_state=StrategyState.DEGRADED,
                to_state=StrategyState.ACTIVE,
                reason="Recovered health and win rate for three consecutive evaluations",
            )

        return None
