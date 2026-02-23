from dataclasses import dataclass
from typing import Dict
import hashlib
import json


@dataclass(frozen=True)
class ExecutionIntent:
    strategy_id: str
    symbol: str
    side: str          # BUY / SELL
    qty: int
    order_type: str    # MARKET / LIMIT
    price: float | None
    meta: Dict

    def intent_id(self) -> str:
        payload = json.dumps(
            {
                "strategy_id": self.strategy_id,
                "symbol": self.symbol,
                "side": self.side,
                "qty": self.qty,
                "order_type": self.order_type,
                "price": self.price,
                "meta": self.meta,
            },
            sort_keys=True,
        )
        return hashlib.sha256(payload.encode()).hexdigest()
