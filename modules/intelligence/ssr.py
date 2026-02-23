from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class TradeResult:
    pnl: float
    status: str  # "FILLED", "CANCELLED", "REJECTED"


class SSRCalculator:
    def compute(self, trades: List[TradeResult]) -> float:
        valid = [t for t in trades if t.status == "FILLED"]

        if not valid:
            return 0.0

        winners = [t for t in valid if t.pnl > 0]

        return round(len(winners) / len(valid), 4)
