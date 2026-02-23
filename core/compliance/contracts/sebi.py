from dataclasses import dataclass
from typing import Dict


@dataclass(frozen=True)
class SEBITradeExport:
    trade_id: str
    strategy_id: str
    symbol: str
    side: str
    quantity: int
    price: float
    timestamp: str  # ISO-8601 UTC

    def to_record(self) -> Dict[str, object]:
        return {
            "trade_id": self.trade_id,
            "strategy_id": self.strategy_id,
            "symbol": self.symbol,
            "side": self.side,
            "quantity": self.quantity,
            "price": self.price,
            "timestamp": self.timestamp,
        }
