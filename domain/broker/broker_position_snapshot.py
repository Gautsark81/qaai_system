from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class BrokerPositionSnapshot:
    symbol: str
    quantity: int
    average_price: float
    market_value: float
    as_of: datetime
