from dataclasses import dataclass
from typing import Dict


@dataclass(frozen=True)
class PaperOrder:
    order_id: str
    symbol: str
    qty: int
    side: str  # BUY / SELL
    price: float


class PaperBroker:
    """
    Stateless paper broker.
    """

    def place_order(self, order: PaperOrder) -> Dict:
        # Immediate fill simulation
        return {
            "order_id": order.order_id,
            "status": "FILLED",
            "filled_qty": order.qty,
            "avg_price": order.price,
        }
