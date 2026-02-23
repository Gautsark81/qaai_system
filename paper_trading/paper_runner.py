"""
Paper Trading Runner
--------------------
Executes paper trading and emits Phase-19 rolling intelligence.
"""

from datetime import datetime
from paper_trading.paper_engine import PaperEngine
from intelligence.paper_adapter import PaperTradingIntelligenceAdapter


class PaperTradingRunner:
    """
    Orchestrates paper trading and Phase-19 intelligence emission.
    """

    def __init__(self):
        self.engine = PaperEngine()
        self.intelligence = PaperTradingIntelligenceAdapter()

    def run(
        self,
        *,
        strategy,
        capital: float,
        start: datetime,
        end: datetime,
    ):
        # 1️⃣ Execute paper trading (existing logic)
        result = self.engine.run(
            strategy=strategy,
            capital=capital,
            start=start,
            end=end,
        )

        # 2️⃣ Phase-19 rolling intelligence (observer-only)
        self.intelligence.process_paper_trades(
            strategy_id=strategy.strategy_id,
            strategy_version=strategy.version,
            trades=result.trades,
            risk_events=result.risk_events,
            execution_stats=result.execution_stats,
            window_start=start,
            window_end=end,
        )

        return result
