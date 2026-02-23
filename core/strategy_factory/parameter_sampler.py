# core/strategy_factory/parameter_sampler.py

import random
from typing import Dict


class ParameterSampler:
    """
    Bounded stochastic sampler (seeded externally).
    """

    @staticmethod
    def sample(indicator: str) -> float:
        bounds = {
            "rsi": (10, 30),
            "zscore": (1.5, 3.0),
            "ema_fast": (5, 20),
            "ema_slow": (30, 100),
            "adx": (20, 35),
            "donchian": (20, 55),
            "atr": (1.2, 3.0),
        }

        lo, hi = bounds[indicator]
        return round(random.uniform(lo, hi), 2)
