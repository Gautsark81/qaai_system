from __future__ import annotations

from core.capital.arming.ledger import CapitalArmingLedger
from core.capital.arming.contracts import CapitalArmingState


class CapitalArmingGate:
    """
    Phase 18.2 — Capital Arming Gate

    HARD GUARANTEES:
    - Read-only
    - Deterministic
    - Ledger is the single source of truth
    - Safe default: capital NOT allowed
    """

    def __init__(self, *, ledger: CapitalArmingLedger):
        self._ledger = ledger

    # ------------------------------------------------------------------
    # Permission Check
    # ------------------------------------------------------------------

    def is_capital_allowed(self) -> bool:
        """
        Return True iff the latest capital arming decision allows capital.
        """

        history = self._ledger.history()

        if not history:
            return False

        latest = history[-1]

        if latest.state == CapitalArmingState.DISARMED:
            return False

        return bool(latest.allowed)
