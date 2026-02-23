from dataclasses import dataclass


@dataclass
class StrategyCapitalState:
    strategy_id: str
    allocated_capital: float
    current_drawdown_pct: float
    ssr: float
