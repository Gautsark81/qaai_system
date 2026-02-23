# utils/signal_provider.py

import logging
from datetime import datetime


class SignalProvider:
    def __init__(self):
        self.logger = logging.getLogger("SignalProvider")
        self.logger.setLevel(logging.INFO)

    def get_signals(self):
        """
        This method returns a list of trade signals.
        Each signal contains:
        - symbol
        - side ('buy' or 'sell')
        - price
        - quantity
        - strategy_id
        - atr (for risk assessment)
        """
        try:
            signals = [
                {
                    "timestamp": datetime.now(),
                    "symbol": "RELIANCE",
                    "side": "buy",
                    "price": 2500,
                    "quantity": 10,
                    "strategy_id": "demo_strategy_v1",
                    "atr": 12.5,
                }
            ]
            self.logger.info(f"Emitting {len(signals)} signal(s)")
            return signals

        except Exception as e:
            self.logger.error(f"[get_signals] Failed to fetch signals: {e}")
            return []
