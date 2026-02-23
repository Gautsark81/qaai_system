from strategies.base import StrategyBase


class DummyStrategy(StrategyBase):
    def __init__(self, config=None):
        super().__init__(config=config)
        self.started_with = None
        self.fills = []

    def on_start(self, context):
        # Ensure base behavior (store context) still happens
        super().on_start(context)
        self.started_with = dict(context)

    def on_bar(self, symbol, bar, features):
        # Simple "if close > open then BUY 1" rule
        if bar.get("close", 0) > bar.get("open", 0):
            return {
                "symbol": symbol,
                "side": "BUY",
                "qty": 1,
                "reason": "close_gt_open",
                "features_snapshot": dict(features),
            }
        return None

    def on_order_filled(self, order, fill):
        self.fills.append((order, fill))


def test_strategy_base_config_and_params():
    s = DummyStrategy(config={"base_size": 2.0, "name": "test_strat"})
    # direct config access
    assert s.config["base_size"] == 2.0
    # get_param with default
    assert s.get_param("base_size") == 2.0
    assert s.get_param("missing_key", 123) == 123

    # set_param should update config
    s.set_param("base_size", 3.0)
    assert s.config["base_size"] == 3.0
    assert s.get_param("base_size") == 3.0


def test_strategy_base_context_storage_on_start():
    ctx = {
        "feature_store": "FS",
        "tick_store": "TS",
        "universe": ["NIFTY", "BANKNIFTY"],
    }
    s = DummyStrategy()
    s.on_start(ctx)

    # context stored as a dict
    assert isinstance(s.context, dict)
    assert s.context["feature_store"] == "FS"
    assert s.context["tick_store"] == "TS"
    # subclass also captured it
    assert s.started_with["universe"] == ["NIFTY", "BANKNIFTY"]


def test_strategy_base_on_bar_and_order_filled():
    s = DummyStrategy()

    bar_up = {"open": 100.0, "close": 101.0}
    bar_flat = {"open": 100.0, "close": 100.0}
    features = {"rsi": 55.0}

    # up bar => returns order dict
    order = s.on_bar("NIFTY", bar_up, features)
    assert order is not None
    assert order["symbol"] == "NIFTY"
    assert order["side"] == "BUY"
    assert order["qty"] == 1
    assert order["reason"] == "close_gt_open"
    assert order["features_snapshot"]["rsi"] == 55.0

    # flat bar => no trade
    no_order = s.on_bar("NIFTY", bar_flat, features)
    assert no_order is None

    # on_order_filled should be callable and record fills
    fill_info = {"qty": 1, "price": 101.0}
    s.on_order_filled(order, fill_info)
    assert len(s.fills) == 1
    recorded_order, recorded_fill = s.fills[0]
    assert recorded_order["symbol"] == "NIFTY"
    assert recorded_fill["price"] == 101.0


def test_strategy_base_on_stop_is_noop():
    s = DummyStrategy()
    # should not raise
    s.on_stop()
