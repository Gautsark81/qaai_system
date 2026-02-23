from __future__ import annotations

from collections import defaultdict
from typing import Dict, List

from core.strategy_factory.promotion.engine import PromotionDecision


# ------------------------------------------------------------------
# Internal Guarded Storage (APPEND-ONLY)
# ------------------------------------------------------------------

class _AppendOnlyStore(defaultdict):
    """
    Internal append-only storage.

    Any destructive mutation attempts raise RuntimeError.
    """

    def clear(self) -> None:  # type: ignore[override]
        raise RuntimeError("PromotionLedger is append-only")

    def pop(self, *args, **kwargs):  # type: ignore[override]
        raise RuntimeError("PromotionLedger is append-only")

    def popitem(self):  # type: ignore[override]
        raise RuntimeError("PromotionLedger is append-only")

    def __delitem__(self, key):  # type: ignore[override]
        raise RuntimeError("PromotionLedger is append-only")


# ------------------------------------------------------------------
# Promotion Ledger
# ------------------------------------------------------------------

class PromotionLedger:
    """
    Phase 17.1 — Promotion Persistence & Audit Trail

    Append-only, immutable, replay-safe ledger
    for PromotionDecision records.
    """

    def __init__(self) -> None:
        # Guarded internal storage
        self._records: Dict[str, List[PromotionDecision]] = _AppendOnlyStore(list)

    # ----------------------------------------------------------
    # Append-only API
    # ----------------------------------------------------------

    def append(self, decision: PromotionDecision) -> None:
        """
        Append a promotion decision to the ledger.

        This operation is:
        - append-only
        - deterministic
        - non-mutating to existing entries
        """
        self._records[decision.strategy_dna].append(decision)

    # ----------------------------------------------------------
    # Read-only API
    # ----------------------------------------------------------

    def history(self, strategy_dna: str) -> List[PromotionDecision]:
        """
        Return ordered promotion history for a strategy.

        Returns a copy to prevent mutation.
        """
        return list(self._records.get(strategy_dna, []))
