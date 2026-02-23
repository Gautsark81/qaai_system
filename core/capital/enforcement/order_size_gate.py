from core.capital.enforcement.contracts import OrderSizeDecision
from core.capital.result import CapitalAllocationResult


class OrderSizeGate:
    """
    Enforces that requested order quantity does not exceed
    capital-derived maximum allowed quantity.

    Policy-free:
    - No pricing logic
    - No capital math
    - No lifecycle awareness
    """

    def enforce(
        self,
        *,
        strategy_id: str,
        requested_qty: int,
        max_allowed_qty: int,
        allocation: CapitalAllocationResult,
    ) -> OrderSizeDecision:
        approved_qty = min(requested_qty, max_allowed_qty)

        reason = (
            "CAPITAL_CAPPED"
            if approved_qty < requested_qty
            else "CAPITAL_APPROVED"
        )

        return OrderSizeDecision(
            strategy_id=strategy_id,
            requested_qty=requested_qty,
            approved_qty=approved_qty,
            reason=reason,
        )
