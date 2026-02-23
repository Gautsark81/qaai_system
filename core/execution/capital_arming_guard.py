from __future__ import annotations

from core.capital.arming.ledger import CapitalArmingLedger


class CapitalArmingEnforcementError(RuntimeError):
    """
    Raised when execution is attempted while capital is not armed.
    """
    pass


class ExecutionCapitalArmingGuard:
    """
    Phase 18.3 — Execution Capital Arming Guard

    HARD GUARANTEES:
    - No mutation
    - No execution logic
    - No capital decisions
    - Deterministic enforcement only
    """

    def __init__(self, *, ledger: CapitalArmingLedger):
        self._ledger = ledger

    # ------------------------------------------------------------------
    # Enforcement
    # ------------------------------------------------------------------

    def enforce(self) -> None:
        """
        Enforce that capital is armed before execution.

        MUST:
        - Raise CapitalArmingEnforcementError if:
            - no arming history exists
            - last decision does not allow execution
        """

        history = self._ledger.history()

        if not history:
            raise CapitalArmingEnforcementError(
                "Execution blocked: no capital arming decision found"
            )

        last_decision = history[-1]

        if not last_decision.allowed:
            raise CapitalArmingEnforcementError(
                "Execution blocked: capital is not armed"
            )

        # Allowed → pass silently
        return None
