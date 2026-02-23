from __future__ import annotations

from typing import Dict, Any


class LedgerInvariantError(RuntimeError):
    """
    Raised when a hard execution / accounting invariant is violated.

    These indicate:
    - corrupted state
    - double accounting
    - broken execution semantics
    """

    pass


def assert_ledger_invariants(
    orders: Dict[str, Dict[str, Any]],
    positions: Dict[str, Dict[str, Any]],
) -> None:
    """
    Enforce HARD ledger invariants.

    This function must:
    - NEVER mutate state
    - NEVER allow silent corruption
    - ALWAYS fail fast on broken accounting

    Called after:
    - replay
    - reconciliation
    - PnL application
    """

    # ==========================================================
    # ORDER INVARIANTS
    # ==========================================================
    for oid, o in orders.items():
        if not isinstance(o, dict):
            raise LedgerInvariantError(f"Order {oid} is not a dict")

        # Quantity must exist and be positive
        qty = o.get("quantity", o.get("position_size"))
        if qty is None or qty <= 0:
            raise LedgerInvariantError(
                f"Invalid quantity for order {oid}: {qty}"
            )

        status = (o.get("status") or "").lower()

        # Closed orders MUST have execution price
        if status == "closed":
            if o.get("price") is None:
                raise LedgerInvariantError(
                    f"Closed order without price: {oid}"
                )

        # Filled quantities must never exceed order quantity
        filled = o.get("filled_qty", 0)
        if filled < 0:
            raise LedgerInvariantError(
                f"Negative filled quantity for order {oid}"
            )

        if filled > qty:
            raise LedgerInvariantError(
                f"Overfilled order {oid}: filled={filled}, qty={qty}"
            )

    # ==========================================================
    # POSITION INVARIANTS
    # ==========================================================
    for symbol, pos in positions.items():
        if not isinstance(pos, dict):
            raise LedgerInvariantError(
                f"Position for {symbol} is not a dict"
            )

        net_qty = pos.get("net_qty", 0)

        # Flat position must have zero exposure
        if net_qty == 0:
            # avg_price MAY be None or zero for flat positions
            continue

        # Non-flat positions MUST have avg_price
        avg_price = pos.get("avg_price")
        if avg_price is None:
            raise LedgerInvariantError(
                f"Position {symbol} has net_qty={net_qty} but missing avg_price"
            )

        if avg_price <= 0:
            raise LedgerInvariantError(
                f"Position {symbol} has invalid avg_price={avg_price}"
            )

    # ==========================================================
    # CROSS-INVARIANTS (ORDER ↔ POSITION)
    # ==========================================================
    # Optional but critical: ensures accounting consistency
    for symbol, pos in positions.items():
        net_qty = pos.get("net_qty", 0)

        # Sum of filled quantities across closed orders
        filled_sum = 0
        for o in orders.values():
            if o.get("symbol") != symbol:
                continue
            if (o.get("status") or "").lower() != "closed":
                continue
            filled_sum += o.get("filled_qty", 0)

        # Net quantity must never exceed historical fills
        if abs(net_qty) > abs(filled_sum):
            raise LedgerInvariantError(
                f"Position {symbol} net_qty={net_qty} exceeds filled_sum={filled_sum}"
            )
