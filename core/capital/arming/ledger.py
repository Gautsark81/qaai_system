from __future__ import annotations

from typing import List, Iterable

from core.capital.arming.contracts import CapitalArmingDecision


# ------------------------------------------------------------------
# Internal: Append-Only Container
# ------------------------------------------------------------------

class _AppendOnlyList(List[CapitalArmingDecision]):
    """
    Internal append-only list.

    Any destructive mutation raises RuntimeError.
    """

    def clear(self) -> None:  # type: ignore[override]
        raise RuntimeError("CapitalArmingLedger is append-only")

    def pop(self, *args, **kwargs):
        raise RuntimeError("CapitalArmingLedger is append-only")

    def remove(self, *args, **kwargs):
        raise RuntimeError("CapitalArmingLedger is append-only")

    def __delitem__(self, *args, **kwargs):
        raise RuntimeError("CapitalArmingLedger is append-only")

    def __setitem__(self, *args, **kwargs):
        raise RuntimeError("CapitalArmingLedger is append-only")


# ------------------------------------------------------------------
# Capital Arming Ledger
# ------------------------------------------------------------------

class CapitalArmingLedger:
    """
    Phase 18.1 — Capital Arming Ledger

    HARD GUARANTEES:
    - Append-only (structurally enforced)
    - Immutable external access
    - Audit & replay safe
    - No side effects
    """

    def __init__(self) -> None:
        self._records: _AppendOnlyList = _AppendOnlyList()

    # ------------------------------------------------------------------
    # Append (ONLY allowed mutation)
    # ------------------------------------------------------------------

    def append(self, decision: CapitalArmingDecision) -> None:
        self._records.append(decision)

    # ------------------------------------------------------------------
    # Read-only history
    # ------------------------------------------------------------------

    def history(self) -> List[CapitalArmingDecision]:
        """
        Return an immutable copy of the arming decision history.
        """
        return list(self._records)
