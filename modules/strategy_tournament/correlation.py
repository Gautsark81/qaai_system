# modules/strategy_tournament/correlation.py

from typing import List
import numpy as np


def pnl_correlation(pnl_a: List[float], pnl_b: List[float]) -> float:
    if len(pnl_a) < 2 or len(pnl_b) < 2:
        return 0.0

    a = np.array(pnl_a)
    b = np.array(pnl_b)

    if a.std() == 0 or b.std() == 0:
        return 0.0

    return float(np.corrcoef(a, b)[0, 1])
