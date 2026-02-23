# modules/qnme/learning.py
from typing import Deque, Any, Dict, List, Tuple
from collections import deque
import random
import time

class ReplayBuffer:
    """
    A simple replay buffer with per-regime partitions.
    """
    def __init__(self, capacity: int = 100000):
        self.capacity = capacity
        self.buf: Deque[Tuple[float, Dict[str, Any]]] = deque(maxlen=capacity)

    def push(self, entry: Dict[str, Any]) -> None:
        """
        entry: {ts, state, action, reward, next_state, regime}
        """
        self.buf.append((time.time(), entry))

    def sample(self, n: int) -> List[Dict[str, Any]]:
        n = min(n, len(self.buf))
        return [entry for (_, entry) in random.sample(list(self.buf), n)]

    def __len__(self):
        return len(self.buf)


class MicroRewardEngine:
    """
    Issues micro-rewards every short window (e.g., 30s).
    Reward shaping includes pnl, drawdown, slippage penalties.
    """
    def __init__(self, pnl_w=1.0, dd_penalty=1.0, slippage_penalty=1.0):
        self.pnl_w = pnl_w
        self.dd_penalty = dd_penalty
        self.slippage_penalty = slippage_penalty

    def compute_reward(self, pnl: float, max_drawdown: float, slippage: float) -> float:
        # reward = pnl - penalty*drawdown - penalty*slippage
        return float(self.pnl_w * pnl - self.dd_penalty * max_drawdown - self.slippage_penalty * slippage)
