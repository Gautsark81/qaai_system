# core/tournament/paper_contracts.py

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, List


@dataclass(frozen=True)
class PaperEvaluation:
    """
    Immutable evaluation result from paper trading.
    """

    run_id: str
    strategy_id: str

    total_trades: int
    win_trades: int
    loss_trades: int

    paper_ssr: float

    slippage_pct: float
    avg_latency_ms: float
    risk_blocks: int

    metrics_version: str
    paper_version: str

    evaluated_at: datetime
    notes: List[str] = field(default_factory=list)

    @staticmethod
    def now_utc() -> datetime:
        return datetime.now(timezone.utc)
