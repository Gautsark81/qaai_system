# strategies/risk_wrapper.py


class RiskProtectedStrategy:
    """
    Wrap an existing strategy instance and call its on_bar only if RiskManager allows.
    If RiskManager denies trading, it will return None (no order).
    """

    def __init__(self, strategy, risk_manager=None):
        self.strategy = strategy
        self.risk = risk_manager

    def on_start(self, context):
        if hasattr(self.strategy, "on_start"):
            self.strategy.on_start(context)

    def on_bar(self, symbol, bar, features):
        # quick check
        try:
            if self.risk is not None and hasattr(self.risk, "is_trading_allowed"):
                # ask risk manager; give account_equity if available
                allowed = True
                try:
                    allowed = self.risk.is_trading_allowed()
                except TypeError:
                    allowed = self.risk.is_trading_allowed(account_equity=None)
                if allowed is False:
                    # do not allow new orders
                    return None
        except Exception:
            # if risk probe fails - default to allowing
            pass
        return self.strategy.on_bar(symbol, bar, features)

    def on_order_filled(self, order, fill):
        if hasattr(self.strategy, "on_order_filled"):
            self.strategy.on_order_filled(order, fill)

    def on_stop(self):
        if hasattr(self.strategy, "on_stop"):
            self.strategy.on_stop()
