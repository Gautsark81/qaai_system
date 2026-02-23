# core/paper_trading/admission.py

from __future__ import annotations

from typing import Optional

from core.operations.arming import ExecutionArming, SystemArmingState
from core.paper_trading.invariants import PaperCapitalDecision


# ------------------------------------------------------------------
# Admission Violation (Paper-Scoped)
# ------------------------------------------------------------------

class PaperExecutionAdmissionViolation(Exception):
    """
    Raised when a paper execution request fails admission checks.

    This exception is:
    - paper-scoped
    - deterministic
    - replay-safe
    - non-mutating
    """
    pass


# ------------------------------------------------------------------
# Paper Execution Admission Gate
# ------------------------------------------------------------------

class PaperExecutionAdmissionGate:
    """
    Phase 14.1 — Paper Execution Admission Gate.

    Responsibilities:
    - Enforce execution arming
    - Validate capital decision presence
    - Validate per-strategy allocation
    - Remain pure and deterministic
    """

    def __init__(self, *, arming: ExecutionArming):
        self._arming = arming

    # --------------------------------------------------------------
    # ADDITIVE: Public arming façade (Phase 14.4 requirement)
    # --------------------------------------------------------------

    @property
    def arming(self) -> ExecutionArming:
        """
        Read-only arming façade.

        Required by Phase 14.4 engine + tests.
        Does NOT alter authority or semantics.
        """
        return self._arming

    # --------------------------------------------------------------
    # Admission Check (UNCHANGED)
    # --------------------------------------------------------------

    def admit(
        self,
        *,
        dna: str,
        capital_decision: Optional[PaperCapitalDecision],
    ) -> None:
        """
        Admit or reject a paper execution request.

        MUST:
        - raise PaperExecutionAdmissionViolation on failure
        - have zero side effects
        - be deterministic
        """

        # ----------------------------------------------------------
        # System arming
        # ----------------------------------------------------------

        if self._arming.state != SystemArmingState.ARMED:
            raise PaperExecutionAdmissionViolation(
                "Paper execution blocked: system is not armed"
            )

        # ----------------------------------------------------------
        # Capital decision presence
        # ----------------------------------------------------------

        if capital_decision is None:
            raise PaperExecutionAdmissionViolation(
                "Paper execution blocked: missing capital decision"
            )

        # ----------------------------------------------------------
        # Allocation check
        # ----------------------------------------------------------

        allocation = capital_decision.allocations.get(dna)

        if allocation is None:
            raise PaperExecutionAdmissionViolation(
                f"Paper execution blocked: no allocation for strategy {dna}"
            )

        if allocation.allocated_fraction <= 0.0:
            raise PaperExecutionAdmissionViolation(
                f"Paper execution blocked: zero allocation for strategy {dna}"
            )

        # ----------------------------------------------------------
        # Admission successful
        # ----------------------------------------------------------
        return None
