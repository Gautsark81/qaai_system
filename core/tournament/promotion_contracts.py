# core/tournament/promotion_contracts.py

from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class PromotionDecision:
    strategy_id: str
    promoted: bool
    reasons: List[str]


@dataclass(frozen=True)
class PromotionThresholds:
    min_ssr: float = 0.80
    min_trades: int = 200
    max_drawdown_pct: float = 15.0
    max_single_loss_pct: float = 5.0
