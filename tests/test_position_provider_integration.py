# tests/test_position_provider_integration.py
import pytest
from qaai_system.execution.paper_provider import PaperExecutionProvider


def test_provider_position_manager_fifo_integration():
    p = PaperExecutionProvider(pm_method="fifo")
    # buy 100 @ 10
    oid1 = p.submit_order({"symbol": "X", "qty": 100, "side": "buy", "price": 10.0})
    st1 = p.get_order_status(oid1)
    assert st1["status"] == "FILLED"
    assert st1["realized_pnl"] == 0.0

    # buy 50 @ 12
    oid2 = p.submit_order({"symbol": "X", "qty": 50, "side": "buy", "price": 12.0})
    st2 = p.get_order_status(oid2)
    assert st2["realized_pnl"] == 0.0

    # sell 120 @ 15
    oid3 = p.submit_order({"symbol": "X", "qty": 120, "side": "sell", "price": 15.0})
    st3 = p.get_order_status(oid3)
    # realized should be 560 (see fifo test)
    assert pytest.approx(st3["realized_pnl"], rel=1e-9) == 560.0

    # positions mapping should reflect net qty (30)
    positions = p.get_positions()
    assert positions["X"] == 30


def test_provider_avg_integration():
    p = PaperExecutionProvider(pm_method="avg")
    p.submit_order({"symbol": "Y", "qty": 100, "side": "buy", "price": 10.0})
    p.submit_order({"symbol": "Y", "qty": 100, "side": "buy", "price": 12.0})
    st = p.submit_order({"symbol": "Y", "qty": 50, "side": "sell", "price": 15.0})
    # Query last order (we only need to ensure method ran without explosion)
    # Confirm positions qty reduced
    positions = p.get_positions()
    assert positions["Y"] == 150
