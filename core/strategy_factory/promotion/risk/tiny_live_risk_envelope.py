from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TinyLiveRiskEnvelope:
    """
    Phase 11.5 — Tiny Live Risk Envelope

    Descriptive, immutable risk bounds for Tiny Live.
    This object has NO authority to enforce, execute, or allocate.
    """

    max_capital: float
    max_position_pct: float
    max_daily_loss_pct: float
    max_order_value: float

    def describe(self) -> str:
        """
        Human-readable description for audit / dashboard only.
        """
        return (
            f"TinyLiveRiskEnvelope("
            f"max_capital={self.max_capital}, "
            f"max_position_pct={self.max_position_pct}, "
            f"max_daily_loss_pct={self.max_daily_loss_pct}, "
            f"max_order_value={self.max_order_value})"
        )
