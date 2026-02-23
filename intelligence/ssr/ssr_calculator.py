from dataclasses import dataclass
from typing import List, Any


MIN_TRADES = 10  # governance invariant


@dataclass(frozen=True)
class SSRResult:
    total_trades: int
    successful_trades: int
    ssr: float
    valid: bool


class SSRCalculator:
    """
    Strategy Success Ratio (SSR)

    Governance rules:
    - valid = False if total_trades < MIN_TRADES
    """

    @staticmethod
    def _value(trade: Any) -> float:
        for attr in ("pnl", "result", "net_r"):
            if hasattr(trade, attr):
                return float(getattr(trade, attr))
        raise AttributeError(
            "Trade object must expose pnl | result | net_r"
        )

    @classmethod
    def compute(cls, trades: List[Any]) -> SSRResult:
        total = len(trades)

        if total == 0:
            return SSRResult(0, 0, 0.0, False)

        successful = sum(1 for t in trades if cls._value(t) > 0)
        ssr = round(successful / total, 4)

        valid = total >= MIN_TRADES

        return SSRResult(
            total_trades=total,
            successful_trades=successful,
            ssr=ssr,
            valid=valid,
        )
