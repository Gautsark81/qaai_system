from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class LivePromotionThresholds:
    min_paper_ssr: float = 0.80
    min_trades: int = 100
    max_slippage_pct: float = 0.30
    max_latency_ms: float = 250.0
    max_risk_blocks: int = 0


@dataclass(frozen=True)
class LivePromotionDecision:
    run_id: str
    strategy_id: str
    promoted: bool
    reasons: List[str]
