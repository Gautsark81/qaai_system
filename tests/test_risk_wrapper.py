# tests/test_risk_wrapper.py
from strategies.risk_wrapper import RiskProtectedStrategy


class DummyStrategy:
    def __init__(self):
        self.calls = []

    def on_start(self, ctx):
        self.calls.append(("start", ctx))

    def on_bar(self, symbol, bar, features):
        self.calls.append(("bar", symbol, bar))
        # always return a simple order
        return {
            "symbol": symbol,
            "side": "buy",
            "quantity": 1,
            "price": bar.get("close", 0),
        }

    def on_order_filled(self, order, fill):
        self.calls.append(("filled", order, fill))

    def on_stop(self):
        self.calls.append(("stop", None))


class AllowRisk:
    def is_trading_allowed(self, account_equity=None):
        return True


class DenyRisk:
    def is_trading_allowed(self, account_equity=None):
        return False


def test_risk_wrapper_allows_when_allowed():
    ds = DummyStrategy()
    wrapper = RiskProtectedStrategy(ds, risk_manager=AllowRisk())
    wrapper.on_start({"symbol": "X"})
    ord = wrapper.on_bar("X", {"close": 10}, {})
    assert ord is not None
    wrapper.on_order_filled({"symbol": "X"}, {"status": "filled"})
    wrapper.on_stop()
    # ensure our dummy strategy received calls
    assert any(c[0] == "bar" for c in ds.calls)


def test_risk_wrapper_blocks_when_denied():
    ds = DummyStrategy()
    wrapper = RiskProtectedStrategy(ds, risk_manager=DenyRisk())
    wrapper.on_start({"symbol": "X"})
    ord = wrapper.on_bar("X", {"close": 10}, {})
    assert ord is None
    # ensure on_bar of underlying strategy was not invoked (no "bar" in calls)
    assert all(c[0] != "bar" for c in ds.calls)
