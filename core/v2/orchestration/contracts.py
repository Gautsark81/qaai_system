# core/v2/orchestration/contracts.py
from dataclasses import dataclass
from typing import List, Dict


@dataclass(frozen=True)
class StrategyCandidate:
    strategy_id: str
    parameters: Dict
    source: str  # generator name


@dataclass(frozen=True)
class BacktestResult:
    strategy_id: str
    ssr: float
    pnl: float
    drawdown: float
    trades: int


@dataclass(frozen=True)
class TournamentResult:
    strategy_id: str
    alpha_score: float
    verdict: str
