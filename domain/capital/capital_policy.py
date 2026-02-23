from dataclasses import dataclass


@dataclass(frozen=True)
class CapitalPolicy:
    max_total_capital: float
    max_per_strategy_pct: float
    max_per_symbol_pct: float
    max_drawdown_pct: float
    min_ssr: float
