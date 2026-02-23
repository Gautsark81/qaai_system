from dataclasses import dataclass


@dataclass(frozen=True)
class OrderSizeDecision:
    """
    Immutable result of capital enforcement on order size.

    This object is:
    - Deterministic
    - Replay-safe
    - Audit-friendly
    """

    strategy_id: str
    requested_qty: int
    approved_qty: int
    reason: str
