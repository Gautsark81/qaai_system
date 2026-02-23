from dataclasses import dataclass


@dataclass(frozen=True)
class LiveTradingConfig:
    enabled: bool
    max_capital_per_strategy: float
    max_daily_loss: float
