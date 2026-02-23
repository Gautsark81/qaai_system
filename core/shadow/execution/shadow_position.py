# core/shadow/execution/shadow_position.py
from dataclasses import dataclass


@dataclass
class ShadowPosition:
    symbol: str
    quantity: int = 0
    avg_price: float = 0.0

    def apply_fill(self, fill_qty: int, fill_price: float) -> None:
        if self.quantity + fill_qty == 0:
            self.quantity = 0
            self.avg_price = 0.0
            return

        total_value = self.avg_price * self.quantity + fill_price * fill_qty
        self.quantity += fill_qty
        self.avg_price = total_value / self.quantity
