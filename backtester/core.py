import pandas as pd
import numpy as np


class BacktestExecution:
    def __init__(
        self,
        slippage_bps: float = 0.0,
        spread_bps: float = 0.0,
    ):
        self.slippage_bps = slippage_bps
        self.spread_bps = spread_bps

    def simulate_series(self, prices: pd.Series):
        slippage = prices * (self.slippage_bps / 10_000.0)
        spread = prices * (self.spread_bps / 10_000.0)

        executed = prices + slippage + spread
        return executed
