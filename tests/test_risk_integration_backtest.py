# tests/test_risk_integration_backtest.py
import pytest
from providers.dhan_provider import DhanProvider
from providers.unified_provider import UnifiedProvider
from infra.order_queue import OrderQueue
from backtest.engine import BacktestEngine
from backtest.position_manager import SimplePositionManager
from data.indicators import build_features_from_ohlcv


class DenyRisk:
    def is_trading_allowed(self, account_equity=None):
        return False


# minimal AlwaysBuyStrategy omitted — reuse simple inline strategy
def test_engine_blocks_when_provider_risk_blocks():
    base = DhanProvider(config={"starting_cash": 10000})
    base.connect()
    base.set_risk_manager(DenyRisk())
    up = UnifiedProvider(
        paper_provider=base, live_provider=None, default_mode="paper", risk_manager=None
    )
    oq = OrderQueue(provider=up, risk_manager=None)

    # Forwarding provider used by engine to route into OrderQueue
    class Fwd:
        def __init__(self, base, oq):
            self.base = base
            self.oq = oq

        def submit_order(self, order):
            return self.oq.submit(order)

        def get_account_nav(self):
            return self.base.get_account_nav()

        def get_positions(self):
            return self.base.get_positions()

        def connect(self):
            return True

        def is_connected(self):
            return True

    fwd = Fwd(base, oq)

    # tiny strategy that buys once
    class S:
        def on_bar(self, symbol, bar, features):
            return {
                "symbol": symbol,
                "side": "buy",
                "quantity": 1,
                "price": bar.get("close"),
            }

    strat = S()
    pm = SimplePositionManager(provider=fwd)
    engine = BacktestEngine(strategy=strat, provider=fwd, position_manager=pm)
    ohlcv = {"TST": [{"open": 1, "high": 2, "low": 0.5, "close": 1.0, "volume": 10}]}
    feats = {
        "TST": build_features_from_ohlcv(
            ohlcv["TST"], ema_periods=[3], rsi_period=3, atr_period=3
        )
    }
    with pytest.raises(ValueError, match="Trading not allowed"):
        engine.run(ohlcv, feats)
