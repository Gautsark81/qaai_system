from __future__ import annotations
from typing import Dict


class ExposureSimulator:
    """
    Detects exposure concentration risk.
    """

    MAX_SYMBOL_EXPOSURE = 0.4

    def evaluate(self, exposures: Dict[str, float]) -> bool:
        """
        exposures: symbol -> % of capital
        returns True if safe, False if dangerous
        """
        for symbol, weight in exposures.items():
            if weight > self.MAX_SYMBOL_EXPOSURE:
                return False
        return True
