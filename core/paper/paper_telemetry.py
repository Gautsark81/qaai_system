# core/paper/paper_telemetry.py

from datetime import datetime
from core.paper.paper_ledger import PaperLedger


class PaperTelemetry:
    """
    High-level telemetry interface.
    """

    def __init__(self):
        self.ledger = PaperLedger()

    def record_rejection(
        self,
        strategy_id: str,
        symbol: str,
        reason: str,
    ):
        self.ledger.log_rejection(
            {
                "timestamp": datetime.utcnow().isoformat(),
                "strategy_id": strategy_id,
                "symbol": symbol,
                "reason": reason,
            }
        )

    def record_fill(self, fill):
        self.ledger.log_trade(fill)
