# modules/strategy/examples.py
from __future__ import annotations
from collections import deque
from typing import Deque, Dict, Iterable, List, Optional

from modules.strategy.base import Signal, Strategy
from modules.strategy.factory import register_strategy


@register_strategy("MeanReversionStrategy")
class MeanReversionStrategy:
    """
    Very small mean-reversion example:
    - keeps a rolling window of `price` values (window size from config)
    - computes z-score = (price - mean) / std
    - if z <= -z_entry -> BUY (size=units); if z >= z_entry -> SELL
    - exit when z crosses zero (optional basic logic)
    Config params:
      - window: int
      - z_entry: float
      - size: float
    """
    def __init__(self, strategy_id: str, config: Dict[str, object]):
        self.strategy_id = strategy_id
        self.window = int(config.get("window", 20))
        self.z_entry = float(config.get("z_entry", 1.5))
        self.size = float(config.get("size", 1.0))
        self._prices: Deque[float] = deque(maxlen=self.window)
        self._last_signal: Optional[Signal] = None

    def prepare(self, historical_features: Iterable[Dict[str, object]]) -> None:
        self._prices.clear()
        for r in historical_features:
            p = r.get("price")
            if p is not None:
                self._prices.append(float(p))

    def _mean_std(self):
        if len(self._prices) == 0:
            return None, None
        data = list(self._prices)
        mean = sum(data) / len(data)
        # sample std
        var = sum((x - mean) ** 2 for x in data) / len(data)
        std = var ** 0.5
        return mean, std

    def generate_signals(self, latest_features: Dict[str, object]) -> List[Signal]:
        p = latest_features.get("price")
        if p is None:
            return []
        p = float(p)
        # update window
        self._prices.append(p)
        mean, std = self._mean_std()
        if mean is None or (std is not None and std == 0.0):
            return []

        z = (p - mean) / (std or 1.0)
        signals = []
        if z <= -self.z_entry:
            signals.append(Signal(strategy_id=self.strategy_id, symbol=str(latest_features["symbol"]), side="BUY", size=self.size, score=-z, meta={"z": z}))
        elif z >= self.z_entry:
            signals.append(Signal(strategy_id=self.strategy_id, symbol=str(latest_features["symbol"]), side="SELL", size=self.size, score=z, meta={"z": z}))
        # The strategy is intentionally simple; no explicit exit logic here.
        return signals


@register_strategy("MomentumStrategy")
class MomentumStrategy:
    """
    Small momentum strategy using two moving averages (fast/slow).
    Emits BUY when fast_ma crosses above slow_ma, SELL on cross below.
    Config:
      - fast: int
      - slow: int
      - size: float
    """
    def __init__(self, strategy_id: str, config: Dict[str, object]):
        self.strategy_id = strategy_id
        self.fast = int(config.get("fast", 5))
        self.slow = int(config.get("slow", 20))
        self.size = float(config.get("size", 1.0))
        self._fast_buf = []
        self._slow_buf = []
        self._last_signal = None

    def prepare(self, historical_features: Iterable[Dict[str, object]]) -> None:
        self._fast_buf = []
        self._slow_buf = []
        for r in historical_features:
            p = r.get("price")
            if p is not None:
                self._fast_buf.append(float(p))
                self._slow_buf.append(float(p))
                if len(self._fast_buf) > self.fast:
                    self._fast_buf.pop(0)
                if len(self._slow_buf) > self.slow:
                    self._slow_buf.pop(0)

    def _ma(self, buf):
        if not buf:
            return None
        return sum(buf) / len(buf)

    def generate_signals(self, latest_features: Dict[str, object]) -> List[Signal]:
        p = latest_features.get("price")
        if p is None:
            return []
        p = float(p)
        self._fast_buf.append(p)
        self._slow_buf.append(p)
        if len(self._fast_buf) > self.fast:
            self._fast_buf.pop(0)
        if len(self._slow_buf) > self.slow:
            self._slow_buf.pop(0)

        fast_ma = self._ma(self._fast_buf)
        slow_ma = self._ma(self._slow_buf)
        if fast_ma is None or slow_ma is None:
            return []

        # detect cross
        signals = []
        if fast_ma > slow_ma:
            signals.append(Signal(strategy_id=self.strategy_id, symbol=str(latest_features["symbol"]), side="BUY", size=self.size, score=float(fast_ma - slow_ma)))
        elif fast_ma < slow_ma:
            signals.append(Signal(strategy_id=self.strategy_id, symbol=str(latest_features["symbol"]), side="SELL", size=self.size, score=float(slow_ma - fast_ma)))
        return signals
