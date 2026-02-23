from dataclasses import dataclass


@dataclass(frozen=True)
class CanaryLimits:
    max_daily_loss_pct: float = 0.50
    max_drawdown_pct: float = 1.00
    max_trades_per_day: int = 5
