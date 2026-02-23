from dataclasses import dataclass
from typing import Dict, Any


@dataclass(frozen=True)
class ShadowFill:
    status: str
    filled_qty: int
    price: float
    reason: str


def always_fill(order: Dict[str, Any]) -> ShadowFill:
    """
    Deterministic shadow fill policy.
    Always fills the requested quantity at the given price.
    """
    qty = int(order.get("quantity", 0))
    price = float(order.get("price", 0.0))

    return ShadowFill(
        status="FILLED",
        filled_qty=qty,
        price=price,
        reason="Shadow fill (deterministic)",
    )
