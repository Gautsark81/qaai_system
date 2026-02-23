# backtest/backtest_price_feed.py

import pandas as pd
import os


class BacktestPriceFeed:
    def __init__(self, data_dir="data/historical", symbols=None, bar_interval="1min"):
        self.data_dir = data_dir
        self.bar_interval = bar_interval
        self.symbols = symbols or []
        self.data = {}
        self.current_index = {}

        self._load_data()

    def _load_data(self):
        for symbol in self.symbols:
            path = os.path.join(self.data_dir, f"{symbol}_{self.bar_interval}.csv")
            if not os.path.exists(path):
                raise FileNotFoundError(f"Data file not found: {path}")
            df = pd.read_csv(path, parse_dates=["timestamp"])
            df = df.sort_values("timestamp").reset_index(drop=True)
            self.data[symbol] = df
            self.current_index[symbol] = 0

    def get_ltp(self, symbol):
        if symbol not in self.data or self.current_index[symbol] >= len(
            self.data[symbol]
        ):
            return None
        return self.data[symbol].iloc[self.current_index[symbol]]["close"]

    def get_bar(self, symbol):
        if symbol not in self.data or self.current_index[symbol] >= len(
            self.data[symbol]
        ):
            return None
        return self.data[symbol].iloc[self.current_index[symbol]].to_dict()

    def next_bar(self):
        for symbol in self.symbols:
            self.current_index[symbol] += 1

    def has_next(self):
        return all(
            self.current_index[symbol] < len(self.data[symbol])
            for symbol in self.symbols
        )

    def get_timestamp(self):
        if not self.symbols:
            return None
        sample_symbol = self.symbols[0]
        return self.data[sample_symbol].iloc[self.current_index[sample_symbol]][
            "timestamp"
        ]
