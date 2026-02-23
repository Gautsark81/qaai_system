# modules/qnme/risk.py
from typing import List
import statistics
import math

class RiskEngine:
    """
    Layer 9: Risk Intelligence Engine
    Simple, mostly offline/online stats here.
    """

    def __init__(self):
        self.returns: List[float] = []
        self.position_notional = 0.0
        self.hard_var_limit = 0.05  # example fraction
        self.halt_flag = False

    def update_returns(self, r: float) -> None:
        self.returns.append(r)
        if len(self.returns) > 10000:
            self.returns.pop(0)

    def cvar(self, alpha: float = 0.95) -> float:
        if not self.returns:
            return 0.0
        sorted_r = sorted(self.returns)
        idx = max(0, int((1.0 - alpha) * len(sorted_r)))
        return abs(sum(sorted_r[:idx]) / max(1, idx))

    def compute_var(self) -> float:
        # sample: standard deviation as proxy
        if len(self.returns) <= 2:
            return 0.0
        return float(statistics.pstdev(self.returns))

    def should_halt(self) -> bool:
        if self.cvar(0.95) > self.hard_var_limit:
            self.halt_flag = True
        return self.halt_flag
