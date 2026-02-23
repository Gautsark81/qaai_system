import numpy as np
import pandas as pd


class StrategyTuner:
    def __init__(self, df: pd.DataFrame):
        self.df = df

    def run(self, n_trials: int = 10):
        # deterministic, optuna-free
        return {
            "rsi_window": 14,
            "atr_window": 14,
        }
