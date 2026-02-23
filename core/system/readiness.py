from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Dict, Optional, Set


# ============================================================
# READINESS ENUMS
# ============================================================

class SystemMode(str, Enum):
    BOOTSTRAP = "BOOTSTRAP"
    PAPER = "PAPER"
    LIVE = "LIVE"
    HALTED = "HALTED"


class ReadinessReason(str, Enum):
    OK = "OK"
    BOOTSTRAP_INCOMPLETE = "BOOTSTRAP_INCOMPLETE"
    GOVERNANCE_NOT_APPROVED = "GOVERNANCE_NOT_APPROVED"
    CAPITAL_NOT_READY = "CAPITAL_NOT_READY"
    EXECUTION_GUARD_BLOCKED = "EXECUTION_GUARD_BLOCKED"
    KILL_SWITCH_ACTIVE = "KILL_SWITCH_ACTIVE"
    MANUAL_HALT = "MANUAL_HALT"


# ============================================================
# READINESS SNAPSHOT
# ============================================================

@dataclass(frozen=True)
class ReadinessSnapshot:
    as_of: datetime
    mode: SystemMode
    is_ready: bool
    blocking_reasons: Set[ReadinessReason]
    metadata: Dict[str, str]


# ============================================================
# READINESS GATE (AUTHORITATIVE)
# ============================================================

class SystemReadinessGate:
    """
    SINGLE AUTHORITATIVE SYSTEM READINESS GATE.

    Guarantees:
    - Deterministic decisions
    - Governance-safe LIVE promotion
    - Kill-switch dominance
    - Replay-safe evaluation
    """

    def evaluate(
        self,
        *,
        now: datetime,
        bootstrap_complete: bool,
        governance_approved: bool,
        capital_ready: bool,
        execution_guard_clear: bool,
        kill_switch_active: bool,
        manual_halt: bool = False,
        requested_mode: Optional[SystemMode] = None,
    ) -> ReadinessSnapshot:

        reasons: Set[ReadinessReason] = set()

        # --------------------------------------------------
        # HARD STOPS (ABSOLUTE DOMINANCE)
        # --------------------------------------------------
        if kill_switch_active:
            reasons.add(ReadinessReason.KILL_SWITCH_ACTIVE)

        if manual_halt:
            reasons.add(ReadinessReason.MANUAL_HALT)

        # --------------------------------------------------
        # BOOTSTRAP SAFETY
        # --------------------------------------------------
        if not bootstrap_complete:
            reasons.add(ReadinessReason.BOOTSTRAP_INCOMPLETE)

        # --------------------------------------------------
        # EXECUTION SAFETY
        # --------------------------------------------------
        if not execution_guard_clear:
            reasons.add(ReadinessReason.EXECUTION_GUARD_BLOCKED)

        # --------------------------------------------------
        # CAPITAL SAFETY
        # --------------------------------------------------
        if not capital_ready:
            reasons.add(ReadinessReason.CAPITAL_NOT_READY)

        # --------------------------------------------------
        # GOVERNANCE LAW (LIVE ONLY)
        # --------------------------------------------------
        if requested_mode == SystemMode.LIVE and not governance_approved:
            reasons.add(ReadinessReason.GOVERNANCE_NOT_APPROVED)

        # --------------------------------------------------
        # FINAL MODE RESOLUTION
        # --------------------------------------------------
        if reasons:
            return ReadinessSnapshot(
                as_of=now,
                mode=SystemMode.HALTED,
                is_ready=False,
                blocking_reasons=reasons,
                metadata={},
            )

        # --------------------------------------------------
        # SAFE MODE SELECTION
        # --------------------------------------------------
        final_mode = requested_mode or SystemMode.PAPER

        return ReadinessSnapshot(
            as_of=now,
            mode=final_mode,
            is_ready=True,
            blocking_reasons={ReadinessReason.OK},
            metadata={},
        )
