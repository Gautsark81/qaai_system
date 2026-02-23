# core/execution/restart_guard.py

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict


# ---------------------------------------------------------------------
# Decision Object (Immutable)
# ---------------------------------------------------------------------

@dataclass(frozen=True)
class RestartDecision:
    allowed: bool
    freeze: bool
    reason: str


# ---------------------------------------------------------------------
# Restart Guard (Cold Start Reconciliation)
# ---------------------------------------------------------------------

class RestartGuard:
    """
    Institutional Cold Restart Reconciliation Guard.

    Ensures broker positions match internal ledger before execution resumes.

    Properties:
    - Deterministic
    - Strict comparison (no tolerance drift)
    - Symbol-normalized
    - Zero-quantity cleaned
    - Freeze-first enforcement
    """

    # =============================================================
    # PUBLIC API
    # =============================================================

    def validate_positions(
        self,
        *,
        internal_positions: Dict[str, float],
        broker_positions: Dict[str, float],
    ) -> RestartDecision:

        internal_clean = self._normalize(internal_positions)
        broker_clean = self._normalize(broker_positions)

        if internal_clean == broker_clean:
            return RestartDecision(
                allowed=True,
                freeze=False,
                reason="RESTART_POSITIONS_MATCH",
            )

        # Build detailed mismatch reason
        mismatch_reason = self._build_mismatch_reason(
            internal_clean,
            broker_clean,
        )

        return RestartDecision(
            allowed=False,
            freeze=True,
            reason=f"POSITION_MISMATCH: {mismatch_reason}",
        )

    # =============================================================
    # INTERNAL HELPERS
    # =============================================================

    def _normalize(self, positions: Dict[str, float]) -> Dict[str, float]:
        """
        Normalize:
        - Remove zero-quantity entries
        - Uppercase symbols
        """

        normalized = {}

        for symbol, qty in positions.items():
            if qty == 0:
                continue

            normalized[symbol.upper()] = float(qty)

        return normalized

    def _build_mismatch_reason(
        self,
        internal: Dict[str, float],
        broker: Dict[str, float],
    ) -> str:
        """
        Construct deterministic mismatch explanation.
        """

        internal_symbols = set(internal.keys())
        broker_symbols = set(broker.keys())

        extra_in_broker = broker_symbols - internal_symbols
        missing_in_broker = internal_symbols - broker_symbols

        quantity_mismatch = []

        for symbol in internal_symbols & broker_symbols:
            if internal[symbol] != broker[symbol]:
                quantity_mismatch.append(symbol)

        parts = []

        if extra_in_broker:
            parts.append(f"EXTRA_BROKER:{sorted(extra_in_broker)}")

        if missing_in_broker:
            parts.append(f"MISSING_BROKER:{sorted(missing_in_broker)}")

        if quantity_mismatch:
            parts.append(f"QTY_DIFF:{sorted(quantity_mismatch)}")

        return "|".join(parts) if parts else "UNKNOWN_MISMATCH"