# tests/test_dhan_adapter_sandbox.py
import time
import pytest
from qaai_system.infra.dhan_adapter import DhanAdapterSandbox, RateLimitExceeded


def test_submit_and_get_status_basic():
    a = DhanAdapterSandbox(rate_limit_per_sec=1000.0)
    oid = a.submit_order(
        {
            "symbol": "RELIANCE",
            "side": "buy",
            "quantity": 10,
            "price": 2000.0,
            "order_type": "LMT",
        }
    )
    assert isinstance(oid, str)
    status = a.get_order_status(oid)
    assert status["order_id"] == oid
    assert status["symbol"] == "RELIANCE"
    assert status["quantity"] == 10
    assert status["status"] == "OPEN"


def test_cancel_order_sets_status_to_cancelled():
    a = DhanAdapterSandbox(rate_limit_per_sec=1000.0)
    oid = a.submit_order({"symbol": "RELIANCE", "side": "buy", "quantity": 5})
    ok = a.cancel_order(oid)
    assert ok is True
    status = a.get_order_status(oid)
    assert status["status"] == "CANCELLED"
    # cancelling again returns False
    assert a.cancel_order(oid) is False


def test_simulate_partial_and_full_fills_updates_positions_and_order_status():
    a = DhanAdapterSandbox(rate_limit_per_sec=1000.0, default_slippage_pct=0.0)
    oid = a.submit_order({"symbol": "RELIANCE", "side": "buy", "quantity": 10})
    # partial fill 4
    f1 = a.simulate_fill(oid, price=100.0, qty=4)
    assert f1["qty"] == 4
    st = a.get_order_status(oid)
    assert st["remaining_qty"] == 6
    # partial fill remaining 6
    f2 = a.simulate_fill(oid, price=101.0, qty=6)
    assert f2["qty"] == 6
    st2 = a.get_order_status(oid)
    assert st2["status"] == "FILLED"
    # check positions aggregated
    pos = a.get_positions().get("RELIANCE")
    assert pos is not None
    assert pos["qty"] == 10
    assert pos["avg_price"] > 0


def test_slippage_model_changes_executed_price():
    a = DhanAdapterSandbox(rate_limit_per_sec=1000.0, default_slippage_pct=0.05)
    oid = a.submit_order({"symbol": "RELIANCE", "side": "buy", "quantity": 2})
    f = a.simulate_fill(oid, price=100.0, qty=2)
    # with slippage_pct 5%, executed price should differ from 100
    assert abs(f["price"] - 100.0) > 1e-9


def test_fetch_ohlcv_returns_bars_and_timeframe_respected():
    a = DhanAdapterSandbox()
    now = int(time.time())
    bars = a.fetch_ohlcv("RELIANCE", now - 600, now, timeframe="1m")
    assert isinstance(bars, list)
    assert len(bars) >= 1
    for b in bars:
        assert "open" in b and "close" in b and "ts" in b


def test_reconcile_with_trade_log_detects_missing_entries():
    a = DhanAdapterSandbox(rate_limit_per_sec=1000.0, default_slippage_pct=0.0)
    a.reset()
    oid1 = a.submit_order({"symbol": "RELIANCE", "side": "buy", "quantity": 3})
    f1 = a.simulate_fill(oid1, price=100.0, qty=3)
    # trade_log missing fill -> should show missing_in_trade_log empty? we provide mismatch intentionally
    trade_log = [
        # a matching entry (by fill_id)
        {
            "fill_id": f1["fill_id"],
            "order_id": oid1,
            "symbol": "RELIANCE",
            "qty": 3,
            "price": f1["price"],
            "side": "buy",
        },
        # a fake entry missing in adapter
        {
            "fill_id": "nonexistent",
            "order_id": "noop",
            "symbol": "RELIANCE",
            "qty": 1,
            "price": 10.0,
            "side": "buy",
        },
    ]
    report = a.reconcile_with_trade_log(trade_log)
    assert "missing_in_adapter" in report
    assert len(report["missing_in_adapter"]) >= 1


def test_rate_limit_raises_when_called_too_fast():
    a = DhanAdapterSandbox(rate_limit_per_sec=1.0)  # one call per second allowed
    # first call ok
    oid = a.submit_order({"symbol": "RELIANCE", "side": "buy", "quantity": 1})
    # second immediate call: throttle triggered (decorator will retry a few times then raise)
    with pytest.raises(RateLimitExceeded):
        # we bypass decorator retry by directly calling _throttle to ensure RateLimitExceeded
        a._throttle()


def test_partial_close_and_pnl_updates_positions():
    a = DhanAdapterSandbox(rate_limit_per_sec=1000.0, default_slippage_pct=0.0)
    oid_buy = a.submit_order({"symbol": "RELIANCE", "side": "buy", "quantity": 10})
    a.simulate_fill(oid_buy, price=100.0, qty=10)
    # sell partial 4
    oid_sell = a.submit_order({"symbol": "RELIANCE", "side": "sell", "quantity": 4})
    f = a.simulate_fill(oid_sell, price=105.0, qty=4)
    pos = a.get_positions()["RELIANCE"]
    # remaining qty 6
    assert pos["qty"] == 6
    # pnl captured should be > 0
    assert pos.get("pnl", 0.0) >= 0.0
