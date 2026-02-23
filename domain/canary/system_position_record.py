from dataclasses import dataclass


@dataclass(frozen=True)
class SystemPositionRecord:
    symbol: str
    quantity: int
    average_price: float
