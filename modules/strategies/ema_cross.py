# modules/strategies/ema_cross.py

from datetime import datetime

from modules.strategies.base import BaseStrategy
from modules.strategies.intent import StrategyIntent


class EMACrossStrategy(BaseStrategy):
    def _run(self, features):
        fast = features["ema_fast"]
        slow = features["ema_slow"]

        if fast == slow:
            return None

        side = "BUY" if fast > slow else "SELL"

        return StrategyIntent(
            strategy_id=self.strategy_id,
            symbol=self.symbol,
            side=side,
            confidence=0.6,
            features_used=["ema_fast", "ema_slow"],
            timestamp=datetime.utcnow(),
        )
