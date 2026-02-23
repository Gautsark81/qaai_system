# tests/test_bracket_manager.py

import pytest
from qaai_system.execution.bracket_manager import BracketManager


class DummyRouter:
    def __init__(self):
        self.submitted = []
        self.canceled = []

    def submit(self, o):
        o = dict(o)
        self.submitted.append(o)
        return o

    def cancel(self, oid):
        self.canceled.append(oid)
        return {"id": oid, "status": "canceled"}

    def dump(self):
        import pprint

        pprint.pp(self.submitted)

    def unique_orders(self):
        """Return list of unique (symbol, side, price, order_type)."""
        seen = set()
        unique = []
        for o in self.submitted:
            key = (o["symbol"], o["side"], round(o["price"], 6), o.get("order_type"))
            if key not in seen:
                seen.add(key)
                unique.append(o)
        return unique


@pytest.fixture
def mgr():
    return BracketManager()


def test_register_and_trigger_take_profit(mgr):
    router = DummyRouter()
    mgr.register(
        symbol="AAA",
        qty=10,
        entry_price=100.0,
        take_profit=110.0,
        stop_loss=95.0,
    )
    mgr.on_fill(
        {"symbol": "AAA", "side": "buy", "quantity": 10, "price": 100.0}, router
    )

    uniq_before = router.unique_orders()

    assert any(
        abs(o["price"] - 110.0) < 1e-6 and o.get("order_type") == "LMT"
        for o in uniq_before
    )
    assert any(
        abs(o["price"] - 95.0) < 1e-6 and o.get("order_type") == "STOP"
        for o in uniq_before
    )

    # After tick, the original TP/SL must still be present, but extra orders are allowed
    mgr.on_tick("AAA", 111.0, router)
    uniq_after = router.unique_orders()

    for o in uniq_before:
        assert o in uniq_after


def test_stop_loss_cancels_take_profit(mgr):
    router = DummyRouter()
    mgr.register(
        symbol="BBB", qty=5, entry_price=50.0, take_profit=60.0, stop_loss=45.0
    )
    mgr.on_fill({"symbol": "BBB", "side": "buy", "quantity": 5, "price": 50.0}, router)

    mgr.on_tick("BBB", 44.0, router)
    uniq = router.unique_orders()
    assert any(o["side"] == "sell" and abs(o["price"] - 45.0) < 1e-6 for o in uniq)
    assert "BBB" not in mgr._brackets


def test_trailing_stop_moves_up_only(mgr):
    router = DummyRouter()
    mgr.register(symbol="CCC", qty=2, entry_price=100.0, trailing_pct=0.1)
    mgr.on_fill({"symbol": "CCC", "side": "buy", "quantity": 2, "price": 100.0}, router)

    mgr.on_tick("CCC", 120.0, router)
    stop_price1 = router.unique_orders()[-1]["price"]

    mgr.on_tick("CCC", 150.0, router)
    stop_price2 = router.unique_orders()[-1]["price"]
    assert stop_price2 > stop_price1

    mgr.on_tick("CCC", 130.0, router)
    stop_price3 = router.unique_orders()[-1]["price"]
    assert stop_price3 == stop_price2


def test_partial_take_profit_reduces_position(mgr):
    router = DummyRouter()
    mgr.register(
        symbol="DDD",
        qty=10,
        entry_price=100.0,
        take_profit=110.0,
        stop_loss=90.0,
    )
    mgr.on_fill(
        {"symbol": "DDD", "side": "buy", "quantity": 10, "price": 100.0}, router
    )
    mgr.on_fill(
        {"symbol": "DDD", "side": "sell", "quantity": 5, "price": 110.0}, router
    )

    assert mgr._brackets["DDD"]["qty"] == 5


def test_trailing_stop_anchor_threshold(mgr):
    router = DummyRouter()
    mgr.register(
        symbol="EEE",
        qty=1,
        entry_price=100.0,
        trailing_pct=0.1,
        anchor_move_pct=0.05,
    )
    mgr.on_fill({"symbol": "EEE", "side": "buy", "quantity": 1, "price": 100.0}, router)

    mgr.on_tick("EEE", 104.0, router)
    uniq = router.unique_orders()
    assert all(o["price"] >= 90.0 for o in uniq if o["side"] == "sell")

    mgr.on_tick("EEE", 120.0, router)
    uniq2 = router.unique_orders()
    assert any(o["price"] > 90.0 for o in uniq2 if o["side"] == "sell")


def test_stop_fill_clears_bracket(mgr):
    router = DummyRouter()
    mgr.register(symbol="FFF", qty=3, entry_price=200.0, stop_loss=180.0)
    mgr.on_fill({"symbol": "FFF", "side": "buy", "quantity": 3, "price": 200.0}, router)

    mgr.on_fill(
        {"symbol": "FFF", "side": "sell", "quantity": 3, "price": 180.0}, router
    )
    assert "FFF" not in mgr._brackets


def test_persistence_roundtrip(mgr):
    mgr.register("GGG", 4, 100.0, take_profit=120.0, stop_loss=90.0)
    state = mgr.save_state()

    mgr2 = BracketManager()
    mgr2.load_state(state)
    assert "GGG" in mgr2._brackets
    assert mgr2._brackets["GGG"]["take_profit"] == 120.0


def test_on_child_fill_reduces_position(mgr):
    router = DummyRouter()
    mgr.register(
        symbol="CHILD",
        qty=10,
        entry_price=100.0,
        take_profit=110.0,
        stop_loss=90.0,
    )
    mgr.on_fill(
        {"symbol": "CHILD", "side": "buy", "quantity": 10, "price": 100.0}, router
    )
    child_fill = {"symbol": "CHILD", "side": "sell", "quantity": 4, "price": 110.0}
    mgr.on_child_fill("CHILD", child_fill, router)

    assert mgr._brackets["CHILD"]["qty"] == 6


def test_trailing_stop_using_atr(mgr):
    router = DummyRouter()
    mgr.register_bracket(
        parent_order_id="ATR_PARENT",
        symbol="ATR",
        side="buy",
        qty=1,
        entry_price=100.0,
        bracket_cfg={
            "trail": {
                "type": "atr",
                "atr_value": 2.0,
                "atr_mult": 2.5,
                "anchor_move_pct": 0.05,
            }
        },
    )
    mgr.on_fill({"symbol": "ATR", "side": "buy", "quantity": 1, "price": 100.0}, router)

    uniq = router.unique_orders()
    assert any(
        abs(o["price"] - 95.0) < 1e-6 and o.get("order_type") == "STOP" for o in uniq
    )


def test_multiple_trailing_ratchets(mgr):
    router = DummyRouter()
    mgr.register(
        symbol="RATCHET",
        qty=1,
        entry_price=100.0,
        trailing_pct=0.1,
        anchor_move_pct=0.05,
    )
    mgr.on_fill(
        {"symbol": "RATCHET", "side": "buy", "quantity": 1, "price": 100.0}, router
    )

    mgr.on_tick("RATCHET", 106.0, router)
    stop1 = router.unique_orders()[-1]["price"]

    mgr.on_tick("RATCHET", 115.0, router)
    stop2 = router.unique_orders()[-1]["price"]

    assert stop2 > stop1


def test_short_side_bracket_behavior(mgr):
    router = DummyRouter()
    mgr.register_bracket(
        parent_order_id="SHORT1",
        symbol="SHORTY",
        side="sell",
        qty=2,
        entry_price=150.0,
        bracket_cfg={
            "take_profits": [{"pct": ((140.0 / 150.0) - 1) * 100, "qty_frac": 1.0}],
            "trail": {
                "type": "percent",
                "trail_pct": 0.1,
                "anchor_move_pct": 0.05,
            },
        },
    )

    # Parent short entry fill
    mgr.on_fill(
        {"symbol": "SHORTY", "side": "sell", "quantity": 2, "price": 150.0}, router
    )

    uniq = router.unique_orders()

    # ✅ Expect TP + SL immediately after entry
    assert any(o["side"] == "buy" and o.get("order_type") == "LMT" for o in uniq)
    assert any(o["side"] == "buy" and o.get("order_type") == "STOP" for o in uniq)


def test_last_price_fallback_logic():
    class DummyOrchestrator:
        def _get_last_price(self, symbol):
            return 99.0

    orchestrator = DummyOrchestrator()
    mgr = BracketManager(orchestrator=orchestrator)
    router = DummyRouter()

    mgr.register(
        symbol="ZZZ", qty=1, entry_price=100.0, trailing_pct=0.1, anchor_move_pct=0.05
    )
    mgr.on_fill({"symbol": "ZZZ", "side": "buy", "quantity": 1, "price": 100.0}, router)

    # Should fallback to last price from orchestrator without crashing
    mgr.on_tick("ZZZ", None, router)


def test_dummyrouter_unique_orders_deduplicates():
    router = DummyRouter()

    # Submit duplicate-looking orders (same symbol, side, price, type)
    router.submit(
        {"symbol": "AAA", "side": "sell", "price": 100.0, "order_type": "LMT"}
    )
    router.submit(
        {"symbol": "AAA", "side": "sell", "price": 100.0, "order_type": "LMT"}
    )
    router.submit(
        {"symbol": "AAA", "side": "sell", "price": 100.0000001, "order_type": "LMT"}
    )  # within rounding

    uniq = router.unique_orders()

    # Only 1 unique order should remain after deduplication
    assert len(uniq) == 1
    assert uniq[0]["symbol"] == "AAA"
    assert uniq[0]["side"] == "sell"
    assert uniq[0]["order_type"] == "LMT"
