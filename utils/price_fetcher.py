# utils/price_fetcher.py

import logging
import random
import os
from infra.dhan_adapter import DhanAdapter


class PriceFetcher:
    def __init__(self):
        self.mode = os.getenv("MODE", "paper").lower()
        self.logger = logging.getLogger("PriceFetcher")

        if self.mode == "dhan":
            self.adapter = DhanAdapter()
        else:
            self.adapter = None

    def get_ltp(self, symbol):
        try:
            if self.mode == "dhan" and self.adapter:
                ltp_data = self.adapter.get_ltp(symbol)
                return float(ltp_data.get("ltp", 0))
            else:
                # Simulate price for paper mode
                price = random.uniform(100, 2500)
                self.logger.debug(f"[Simulated LTP] {symbol}: {price:.2f}")
                return price
        except Exception as e:
            self.logger.warning(
                f"[PriceFetcher] Failed to fetch price for {symbol}: {e}"
            )
            return 0.0
