# demo/demo_strategy.py

from datetime import datetime

from modules.strategies.base import BaseStrategy
from modules.strategies.intent import StrategyIntent


class DemoStrategy(BaseStrategy):
    def _run(self, data):
        return StrategyIntent(
            strategy_id=self.strategy_id,
            symbol="NIFTY",
            side="BUY",
            confidence=0.75,
            features_used=["demo_feature"],
            timestamp=datetime.utcnow(),
        )
