import pandas as pd
import numpy as np


class PortfolioSimulator:
    def __init__(self, initial_cash=1_000_000, max_allocation_per_trade=0.05):
        """
        Initialize the simulator with starting cash and allocation strategy.
        """
        self.initial_cash = initial_cash
        self.cash = initial_cash
        self.max_alloc = max_allocation_per_trade
        self.positions = {}
        self.trade_log = []
        self.portfolio_value = []

    def _buy(self, symbol, price, timestamp, confidence):
        """
        Executes a buy order.
        """
        allocation = self.cash * self.max_alloc * confidence
        qty = int(allocation // price)
        if qty <= 0:
            return

        cost = qty * price
        self.cash -= cost
        self.positions[symbol] = {
            "qty": qty,
            "entry_price": price,
            "timestamp": timestamp,
        }
        self.trade_log.append(
            {
                "timestamp": timestamp,
                "symbol": symbol,
                "action": "BUY",
                "price": float(price),
                "qty": qty,
                "cost": float(cost),
            }
        )

    def _sell(self, symbol, price, timestamp):
        """
        Executes a sell order.
        """
        if symbol not in self.positions:
            return

        qty = self.positions[symbol]["qty"]
        entry_price = self.positions[symbol]["entry_price"]
        pnl = (price - entry_price) * qty
        proceeds = qty * price
        self.cash += proceeds
        del self.positions[symbol]

        self.trade_log.append(
            {
                "timestamp": timestamp,
                "symbol": symbol,
                "action": "SELL",
                "price": float(price),
                "qty": qty,
                "pnl": float(pnl),
                "proceeds": float(proceeds),
            }
        )

    def run(self, signals_df, price_col="price"):
        """
        Runs the portfolio simulation on the provided signal DataFrame.
        """
        for _, row in signals_df.iterrows():
            symbol = row["symbol"]
            signal = row["signal"]
            price = float(row.get(price_col, 100))  # default fallback price
            timestamp = row["timestamp"]
            confidence = float(row.get("confidence", 1.0))

            if signal == "BUY":
                self._buy(symbol, price, timestamp, confidence)
            elif signal == "SELL":
                self._sell(symbol, price, timestamp)

            # Recompute portfolio value
            total_value = self.cash + sum(
                pos["qty"] * price for _, pos in self.positions.items()
            )
            self.portfolio_value.append(
                {"timestamp": timestamp, "value": float(total_value)}
            )

        return pd.DataFrame(self.trade_log), pd.DataFrame(self.portfolio_value)

    def summary(self):
        """
        Returns a performance summary including PnL, Sharpe, drawdown, and final value.
        """
        values = pd.DataFrame(self.portfolio_value)
        if values.empty:
            return {}

        returns = values["value"].pct_change().dropna()
        sharpe = np.mean(returns) / (np.std(returns) + 1e-8) * np.sqrt(252)
        drawdown = (values["value"].cummax() - values["value"]).max()

        final_value = float(values["value"].iloc[-1])
        pnl = float(final_value - self.initial_cash)

        return {
            "final_value": final_value,
            "pnl": pnl,
            "sharpe": round(float(sharpe), 3),
            "max_drawdown": round(float(drawdown), 2),
        }
