from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class BrokerTradeSnapshot:
    order_id: str
    symbol: str
    side: str                 # BUY / SELL
    executed_qty: int
    executed_price: float
    executed_value: float     # ₹
    executed_at: datetime
