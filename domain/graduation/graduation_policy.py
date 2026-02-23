from dataclasses import dataclass


@dataclass(frozen=True)
class GraduationPolicy:
    min_ssr: float
    min_live_days: int
    max_drawdown_pct: float
    min_trades: int
