# core/runtime/system_authorizer.py
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from core.system.readiness import SystemReadinessGate
from core.lifecycle.contracts.state import LifecycleState


class AuthorizationDecision(str, Enum):
    RUN = "RUN"
    HALT = "HALT"


@dataclass(frozen=True)
class RuntimeAuthorizationResult:
    decision: AuthorizationDecision
    reason: str


class SystemAuthorizer:
    """
    Single authoritative runtime authorization gate.

    HARD LAW:
    - If ANY gate blocks → HALT
    - No intelligence
    - No overrides
    - No probabilistic logic

    This class is the ONLY runtime authorizer.
    """

    def __init__(self, *, readiness_gate: SystemReadinessGate) -> None:
        self._readiness_gate = readiness_gate

    # -------------------------------------------------
    # CORE AUTHORIZATION PATH (PRODUCTION)
    # -------------------------------------------------

    def authorize(
        self,
        *,
        lifecycle_state: LifecycleState,
        execution_guard_armed: bool,
    ) -> RuntimeAuthorizationResult:
        # -------------------------------------------------
        # READINESS GATE (ABSOLUTE)
        # -------------------------------------------------
        readiness = self._readiness_gate.evaluate()
        if not readiness.allowed:
            return RuntimeAuthorizationResult(
                decision=AuthorizationDecision.HALT,
                reason=f"Readiness blocked: {readiness.reason}",
            )

        # -------------------------------------------------
        # LIFECYCLE SAFETY
        # -------------------------------------------------
        if lifecycle_state != LifecycleState.LIVE:
            return RuntimeAuthorizationResult(
                decision=AuthorizationDecision.HALT,
                reason=f"Lifecycle state blocks execution: {lifecycle_state.name}",
            )

        # -------------------------------------------------
        # EXECUTION GUARD
        # -------------------------------------------------
        if not execution_guard_armed:
            return RuntimeAuthorizationResult(
                decision=AuthorizationDecision.HALT,
                reason="Execution guard not armed",
            )

        # -------------------------------------------------
        # ALL CLEAR
        # -------------------------------------------------
        return RuntimeAuthorizationResult(
            decision=AuthorizationDecision.RUN,
            reason="System authorized to run",
        )

    # -------------------------------------------------
    # PHASE-AWARE / GOVERNANCE EXTENSIONS (SAFE, READ-ONLY)
    # -------------------------------------------------

    def allow_red_team_observability(self, *, environment, phase: int) -> bool:
        """
        Red-team observability is allowed ONLY when:
        - environment is test
        - phase >= 20

        This method does NOT grant execution authority.
        """
        return getattr(environment, "name", None) == "test" and phase >= 20
