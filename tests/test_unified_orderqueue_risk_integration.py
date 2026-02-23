# tests/test_unified_orderqueue_risk_integration.py
import pytest

from providers.dhan_provider import DhanProvider
from providers.unified_provider import UnifiedProvider
from infra.order_queue import OrderQueue
from backtest.engine import BacktestEngine
from backtest.position_manager import SimplePositionManager
from data.indicators import build_features_from_ohlcv


# Simple forwarding provider that delegates submit_order to an OrderQueue instance
class ForwardingProvider:
    def __init__(self, base_provider, order_queue):
        self.base = base_provider
        self._order_queue = order_queue

    def submit_order(self, order):
        # forward through queue (this will perform risk checks)
        return self._order_queue.submit(order)

    def submit_order_with_retry(self, *a, **k):
        return self.submit_order(*a, **k)

    def get_account_nav(self):
        return self.base.get_account_nav()

    def get_positions(self):
        return self.base.get_positions()

    def connect(self):
        return self.base.connect()

    def is_connected(self):
        return self.base.is_connected()


# Dummy strategy used by engine: always produce a buy order on bar
class AlwaysBuyStrategy:
    def __init__(self, symbol="TST", qty=1, price_key="close"):
        self.symbol = symbol
        self.qty = qty
        self.price_key = price_key

    def on_start(self, ctx):
        pass

    def on_bar(self, symbol, bar, features):
        # return a buy order that should be routed via provider
        return {
            "symbol": symbol,
            "side": "buy",
            "quantity": self.qty,
            "price": float(bar.get(self.price_key, 0)),
        }

    def on_order_filled(self, order, fill):
        pass

    def on_stop(self):
        pass


def make_ohlcv(n=2):
    return [
        {"open": i, "high": i + 0.5, "low": i - 0.5, "close": float(i), "volume": 10}
        for i in range(1, n + 1)
    ]


def test_engine_order_queue_blocks_when_risk_disallows():
    # base provider + unified provider wired with a deny-all risk manager
    base = DhanProvider(config={"starting_cash": 10000})
    base.connect()

    class DenyRisk:
        def is_trading_allowed(self, account_equity=None):
            return False

    deny_rm = DenyRisk()
    up = UnifiedProvider(
        paper_provider=base,
        live_provider=None,
        default_mode="paper",
        risk_manager=deny_rm,
    )

    # OrderQueue uses unified provider and same risk manager
    oq = OrderQueue(
        provider=up,
        throttle_seconds=0.0,
        max_retries=0,
        retry_delay=0.0,
        risk_manager=deny_rm,
    )
    fwd = ForwardingProvider(base_provider=base, order_queue=oq)

    strat = AlwaysBuyStrategy(symbol="TST", qty=1)
    pm = SimplePositionManager(provider=fwd)
    engine = BacktestEngine(strategy=strat, provider=fwd, position_manager=pm)

    ohlcv = {"TST": make_ohlcv(2)}
    features = {
        "TST": build_features_from_ohlcv(
            ohlcv["TST"], ema_periods=[3], rsi_period=3, atr_period=3
        )
    }

    # engine.run should raise due to risk disallowing trading
    with pytest.raises(ValueError, match="Trading not allowed"):
        engine.run(ohlcv, features)


def test_engine_order_queue_enforces_symbol_cap():
    base = DhanProvider(config={"starting_cash": 10000})
    base.connect()
    # set base to have existing large position to trip symbol cap
    base._positions["SYM"] = 45
    base._positions["__last_price__:SYM"] = 100

    class RM:
        def __init__(self):
            # only 5% exposure allowed; existing position is already huge
            self.config = {"max_symbol_weight": 0.05}

        def is_trading_allowed(self, account_equity=None):
            return True

    rm = RM()
    up = UnifiedProvider(
        paper_provider=base,
        live_provider=None,
        default_mode="paper",
        risk_manager=rm,
    )
    oq = OrderQueue(
        provider=up,
        throttle_seconds=0.0,
        max_retries=0,
        retry_delay=0.0,
        risk_manager=rm,
    )
    fwd = ForwardingProvider(base_provider=base, order_queue=oq)

    # strategy will attempt to buy more SYM and should be blocked by symbol cap
    strat = AlwaysBuyStrategy(symbol="SYM", qty=10, price_key="close")
    pm = SimplePositionManager(provider=fwd)
    engine = BacktestEngine(strategy=strat, provider=fwd, position_manager=pm)

    ohlcv = {
        "SYM": [
            {"open": 100, "high": 101, "low": 99, "close": 100.0, "volume": 10},
        ]
    }
    features = {
        "SYM": build_features_from_ohlcv(
            ohlcv["SYM"], ema_periods=[3], rsi_period=3, atr_period=3
        )
    }

    with pytest.raises(ValueError, match="Symbol cap exceeded for SYM"):
        engine.run(ohlcv, features)
