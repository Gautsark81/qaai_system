from __future__ import annotations
import math
import pandas as pd


class PositionSizer:
    """
    ATR-aware position sizing:
      - dollar_risk = equity * risk_pct
      - stop_distance = max(ATR, price * min_stop_pct) * atr_mult
      - size = floor(dollar_risk / stop_distance)
      - notional capped by max_leverage * equity
    """

    def __init__(
        self,
        risk_pct: float = 0.01,
        atr_mult: float = 1.5,
        min_stop_pct: float = 0.0025,  # 0.25% floor
        max_leverage: float = 1.0,
        min_size: int = 1,
    ):
        self.risk_pct = risk_pct
        self.atr_mult = atr_mult
        self.min_stop_pct = min_stop_pct
        self.max_leverage = max_leverage
        self.min_size = min_size

    def compute_from_row(self, row: pd.Series, equity: float) -> int:
        price = float(row["close"])
        atr = float(
            row.get("ATR", price * self.min_stop_pct)
        )  # fallback if ATR missing
        dollar_risk = equity * self.risk_pct
        stop_distance = max(atr, price * self.min_stop_pct) * self.atr_mult
        raw_size = 0 if stop_distance <= 0 else math.floor(dollar_risk / stop_distance)

        # Leverage cap
        max_notional = equity * self.max_leverage
        max_size = math.floor(max_notional / price) if price > 0 else 0
        size = max(self.min_size if raw_size > 0 else 0, min(raw_size, max_size))
        return int(size)
