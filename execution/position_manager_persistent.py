# qaai_system/execution/position_manager_persistent.py
from pathlib import Path
import json
from typing import Optional, Dict, Any
from .position_manager import PositionManager


class PersistentPositionManager(PositionManager):
    """
    Extends PositionManager with persistence.
    Stores all fills in a JSONL file and rebuilds state on restart.
    """

    def __init__(self, method: str = "fifo", store_path: Optional[str] = None):
        self.store_path = Path(store_path) if store_path else None
        super().__init__(method=method)

        # replay persisted fills into state
        if self.store_path and self.store_path.exists():
            with open(self.store_path, "r") as f:
                for line in f:
                    evt = json.loads(line)
                    # note: persist=False to avoid writing again while replaying
                    super().on_fill(
                        evt["symbol"], evt["side"], evt["qty"], evt["price"]
                    )

    def on_fill(self, symbol: str, side: str, qty: int, price: float) -> float:
        realized = super().on_fill(symbol, side, qty, price)
        if self.store_path:
            with open(self.store_path, "a") as f:
                f.write(
                    json.dumps(
                        {"symbol": symbol, "side": side, "qty": qty, "price": price}
                    )
                    + "\n"
                )
        return realized

    def dump_snapshot(self) -> Dict[str, Any]:
        """Return current positions and realized PnL for monitoring."""
        return {sym: self.get_position(sym) for sym in self._lots.keys()}
